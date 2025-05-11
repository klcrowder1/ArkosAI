# Object Detection in Arkos AI

Arkos AI provides powerful object detection capabilities with support for multiple specialized models, allowing for more accurate and efficient detection of different object types.

## Multi-Model Support

Arkos AI supports using multiple specialized models for object detection, each optimized for specific purposes. This allows for more accurate detection of different object types while maintaining efficient resource usage.

### Key Benefits

- **Specialized Detection**: Use models optimized for specific object types (people, vehicles, license plates, etc.)
- **Improved Accuracy**: Specialized models typically provide better accuracy for their target objects
- **Resource Efficiency**: Use higher-resolution models only for specific purposes where needed
- **Flexible Configuration**: Configure which models to use for each camera

### How It Works

1. **Model Registration**: Multiple models are registered with the system, each with a specific purpose
2. **Purpose-Based Selection**: When detecting objects, the appropriate model is selected based on the detection purpose
3. **Result Merging**: Results from multiple models can be merged using different strategies
4. **Camera-Specific Configuration**: Each camera can be configured to use specific model purposes

## Configuration

### Detector Configuration

```yaml
detectors:
  cpu:
    type: cpu
    num_threads: 3
    models:
      # General purpose model (default)
      - path: /models/yolov7-320.pt
        width: 320
        height: 320
        model_type: yologeneric
        purpose: general
        priority: 100
      
      # Person-specific model (higher resolution)
      - path: /models/person-model-640.pt
        width: 640
        height: 640
        model_type: yologeneric
        purpose: person
        priority: 50
```

### Model Parameters

- **path**: Path to the model file
- **width/height**: Input dimensions for the model
- **model_type**: Type of model (yologeneric, ssd, etc.)
- **purpose**: Purpose of the model (general, person, vehicle, etc.)
- **priority**: Priority of the model (lower number = higher priority)

### Camera Configuration

```yaml
cameras:
  front_door:
    detect:
      height: 1080
      width: 1920
      fps: 5
      # Configure which model purposes to use for this camera
      model_purposes:
        - general
        - person
```

## Supported Model Types

Arkos AI supports various model types:

- **YOLOv7/YOLOv8**: High-performance object detection models
- **SSD (Single Shot Detector)**: Fast object detection models
- **YOLO-NAS**: Neural Architecture Search optimized YOLO models
- **Custom Models**: Support for custom-trained models

## Hardware Acceleration

Depending on your hardware, Arkos AI can use different acceleration methods:

- **CPU**: Standard CPU-based inference
- **GPU**: CUDA-accelerated inference for NVIDIA GPUs
- **EdgeTPU**: Google Coral EdgeTPU acceleration
- **TensorRT**: NVIDIA TensorRT acceleration
- **OpenVINO**: Intel Neural Compute Stick and CPU acceleration
- **RKNN**: Rockchip NPU acceleration
- **Hailo**: Hailo AI accelerator support

## Advanced Usage

### Merge Strategies

When using multiple models, detection results can be merged using different strategies:

- **Highest Confidence**: Keep the detection with the highest confidence
- **Specialized First**: Prefer detections from specialized models over general ones
- **All**: Keep all detections from all models

### Custom Model Integration

Arkos AI provides comprehensive support for custom-trained models in various formats, allowing you to use your own specialized models for object detection.

#### Supported Custom Model Formats

- **TensorFlow Lite**: Optimized for edge devices and mobile applications
- **ONNX**: Open Neural Network Exchange format for interoperability between frameworks
- **PyTorch**: Direct loading of PyTorch models

#### Integration Steps

1. **Prepare your model**:
   - Ensure your model is in one of the supported formats (TFLite, ONNX, PyTorch)
   - Prepare a label map that maps class indices to class names

2. **Place your model files**:
   - Create a directory for your custom models (e.g., `/models/custom/`)
   - Copy your model file and any associated files to this directory

3. **Configure the custom model detector**:
   - Add a `custom` detector configuration to your `config.yml`
   - Specify the model format and any preprocessing requirements
   - Configure each model with appropriate parameters (input size, tensor format, etc.)
   - Define the label mapping for your model

4. **Restart Arkos AI** to load the new model configuration

#### Example Configuration

```yaml
detectors:
  custom:
    type: custom
    num_threads: 4
    model_format: "onnx"  # Options: tflite, onnx, pytorch
    # Custom preprocessing configuration
    custom_preprocessing:
      mean: [0.485, 0.456, 0.406]  # RGB mean values for normalization
      std: [0.229, 0.224, 0.225]   # RGB standard deviation values for normalization
      transforms:
        - rgb_to_bgr                # Convert RGB to BGR if needed
        - hwc_to_chw                # Convert HWC to CHW if needed
    # Models configuration
    models:
      # Custom general purpose model
      - path: /models/custom/my-custom-model.onnx
        width: 640
        height: 640
        model_type: yologeneric
        purpose: general
        priority: 100
        input_tensor: nchw         # Input tensor format (nchw or nhwc)
        input_pixel_format: rgb    # Input pixel format (rgb or bgr)
        input_dtype: float         # Input data type (float, float_denorm, or int)
        # Custom label mapping
        labelmap:
          0: person
          1: car
          2: truck
          3: bicycle
          4: motorcycle
          5: bus
```

#### Advanced Custom Model Configuration

The custom model detector provides several configuration options to adapt to different model requirements:

- **Model Format**: Specify the format of your model (`tflite`, `onnx`, or `pytorch`)
- **Custom Preprocessing**: Configure preprocessing steps like normalization, mean subtraction, and format conversions
- **Input Configuration**: Specify input tensor format, pixel format, and data type
- **Label Mapping**: Define custom mappings from class indices to class names
- **Purpose and Priority**: Assign specific purposes to models and set their priority

#### Using Multiple Custom Models

You can configure multiple custom models with different purposes:

```yaml
models:
  # General purpose model
  - path: /models/custom/general-model.onnx
    purpose: general
    priority: 100
    # ... other configuration ...
  
  # Specialized face detection model
  - path: /models/custom/face-model.onnx
    purpose: face
    priority: 50
    # ... other configuration ...
```

Then configure cameras to use specific model purposes:

```yaml
cameras:
  front_door:
    detect:
      # ... other configuration ...
      model_purposes:
        - general
        - face
```

## Performance Considerations

- Use specialized high-resolution models only for specific purposes where needed
- Balance the number of models with available system resources
- Consider using hardware acceleration for better performance
