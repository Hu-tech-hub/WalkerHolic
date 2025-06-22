import tensorflow as tf
import keras
import warnings
# Only suppress specific warnings instead of all
warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')

# TensorFlow 설정
print(f"TensorFlow version: {tf.__version__}")
print(f"Keras version: {keras.__version__}")

# ==== 추론용 커스텀 클래스들 ====================================================

@keras.utils.register_keras_serializable()
class TCNBlock(keras.layers.Layer):
    """Temporal Convolutional Network Block"""
    def __init__(self, filters, kernel_size, dilation_rate, dropout_rate=0.2, **kwargs):
        super().__init__(**kwargs)
        self.filters = filters
        self.kernel_size = kernel_size
        self.dilation_rate = dilation_rate
        self.dropout_rate = dropout_rate

        # main path
        self.conv1 = keras.layers.Conv1D(filters, kernel_size,
                                     dilation_rate=dilation_rate,
                                     padding="causal")
        self.conv2 = keras.layers.Conv1D(filters, kernel_size,
                                     dilation_rate=dilation_rate,
                                     padding="causal")
        self.layernorm1 = keras.layers.LayerNormalization()
        self.layernorm2 = keras.layers.LayerNormalization()
        self.dropout1 = keras.layers.SpatialDropout1D(dropout_rate)
        self.dropout2 = keras.layers.SpatialDropout1D(dropout_rate)
        self.activation = keras.layers.ReLU()

        # residual path
        self.residual_conv = None

    def build(self, input_shape):
        if input_shape[-1] != self.filters:
            self.residual_conv = keras.layers.Conv1D(self.filters, 1, padding="same")
        super().build(input_shape)

    def call(self, inputs, training=False):
        x = self.conv1(inputs)
        x = self.layernorm1(x)
        x = self.activation(x)
        x = self.dropout1(x, training=training)

        x = self.conv2(x)
        x = self.layernorm2(x)
        x = self.activation(x)
        x = self.dropout2(x, training=training)

        # residual add
        residual = self.residual_conv(inputs) if self.residual_conv else inputs
        return residual + x
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'filters': self.filters,
            'kernel_size': self.kernel_size,
            'dilation_rate': self.dilation_rate,
            'dropout_rate': self.dropout_rate
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        return cls(**config)

@keras.utils.register_keras_serializable()
class CausalAttention(keras.layers.Layer):
    """Causal Multi-Head Attention with Dilation"""
    def __init__(self, num_heads=4, key_dim=32, dilation_rate=4, window_size=8, **kwargs):
        super().__init__(**kwargs)
        self.num_heads = num_heads
        self.key_dim = key_dim
        self.dilation_rate = dilation_rate
        self.window_size = window_size

        self.attention = keras.layers.MultiHeadAttention(
            num_heads=num_heads,
            key_dim=key_dim,
            dropout=0.1
        )
        self.layernorm = keras.layers.LayerNormalization()

    def call(self, inputs, training=False):
        batch_size, seq_len, features = tf.shape(inputs)[0], tf.shape(inputs)[1], tf.shape(inputs)[2]

        # Create causal mask with dilation
        mask = self.create_dilated_causal_mask_tf(seq_len)

        # Apply attention
        attn_output = self.attention(
            query=inputs,
            value=inputs,
            key=inputs,
            attention_mask=mask,
            training=training
        )

        # Residual connection with layer norm
        return self.layernorm(inputs + attn_output)

    def create_dilated_causal_mask_tf(self, seq_len):
        """Create dilated causal attention mask"""
        i_indices = tf.range(seq_len, dtype=tf.int32)
        j_indices = tf.range(seq_len, dtype=tf.int32)

        # Create 2D grids
        i_grid, j_grid = tf.meshgrid(i_indices, j_indices, indexing='ij')

        # Condition 1: Causal constraint (j <= i)
        causal_mask = j_grid <= i_grid

        # Condition 2: Window constraint (i - j <= window_size * dilation_rate)
        distance = i_grid - j_grid
        window_mask = distance <= (self.window_size * self.dilation_rate)

        # Condition 3: Dilation constraint ((i - j) % dilation_rate == 0)
        dilation_mask = tf.equal(tf.math.mod(distance, self.dilation_rate), 0)

        # Combine all conditions
        final_mask = tf.logical_and(tf.logical_and(causal_mask, window_mask), dilation_mask)

        return tf.cast(final_mask, tf.bool)
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'num_heads': self.num_heads,
            'key_dim': self.key_dim,
            'dilation_rate': self.dilation_rate,
            'window_size': self.window_size
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        return cls(**config)

# ==== 추론용 모델 클래스 ====================================================

class Stage2Model:
    """Stage 2: DS/SSR/SSL Classification - 추론 전용 버전"""
    def __init__(self, input_shape=(30, 6)):
        self.input_shape = input_shape
        self.model = None

    def build_model(self):
        """Enhanced TCN 모델 구축 - Frame-wise prediction with logits output"""
        inputs = keras.Input(shape=self.input_shape)

        # TCN layers with increasing dilation
        x = TCNBlock(32, kernel_size=3, dilation_rate=1, dropout_rate=0.2)(inputs)
        x = TCNBlock(64, kernel_size=3, dilation_rate=2, dropout_rate=0.2)(x)
        x = TCNBlock(64, kernel_size=3, dilation_rate=4, dropout_rate=0.2)(x)

        # Add Causal Attention after last TCN block
        x = CausalAttention(num_heads=4, key_dim=32, dilation_rate=4, window_size=8)(x)

        # Frame-wise prediction with logits (no softmax to avoid duplication)
        outputs = keras.layers.TimeDistributed(keras.layers.Dense(3, activation=None))(x)  # logits

        self.model = keras.Model(inputs, outputs)
        return self.model

    def load_model(self, model_path):
        """저장된 모델 로드 (데코레이터 기반)"""
        self.model = keras.models.load_model(model_path, compile=False)
        print(f"✅ 모델 로드 완료: {model_path}")
        return self.model

    def predict(self, X):
        """추론 수행"""
        if self.model is None:
            raise ValueError("모델이 로드되지 않았습니다. load_model()을 먼저 호출하세요.")
        
        predictions = self.model.predict(X, verbose=0)
        
        # Softmax 적용 (모델이 logits를 출력하는 경우)
        if predictions.max() > 1.0:  # logits 형태인 경우
            predictions = tf.nn.softmax(predictions, axis=-1).numpy()
        
        return predictions

if __name__ == "__main__":
    print("="*50)
    print("🚀 Stage 2 Model - 추론 전용 버전")
    print("="*50)
    print("📦 포함된 커스텀 클래스:")
    print("   ✅ TCNBlock - Temporal Convolutional Network")
    print("   ✅ CausalAttention - Causal Multi-Head Attention")
    print("   ✅ Stage2Model - 모델 클래스")
    print("")
    print("🎯 사용법:")
    print("   from stage2_model import Stage2Model")
    print("   model = Stage2Model()")
    print("   model.load_model('path/to/model.keras')")
    print("   predictions = model.predict(X)")
    print("="*50)