import numpy as np
import cv2, io, base64
from PIL import Image

def generate_features(implementation_version, draw_graphs, raw_data, axes, sampling_freq, high_threshold, low_threshold, gaussian_blur):
    # features is a 1D array, reshape so we have a matrix
    raw_data = raw_data.reshape(int(len(raw_data) / len(axes)), len(axes))

    graphs = []
    all_features = []

    width = raw_data[0][0]
    height = raw_data[1][0]
    raw_data = raw_data[2:].astype(dtype=np.uint32).view(dtype=np.uint8)

    pixels_per_frame = height * width * 4
    frame_count = 0
    expected_frame_count = len(raw_data) / pixels_per_frame

    for i in np.arange(0, len(raw_data), pixels_per_frame):
        # grab the image (there could be multiple potentially)
        frame = (raw_data.flatten()[i:i+pixels_per_frame]).reshape((height, width, 4))

        # convert into an image
        img = Image.fromarray(frame, mode='RGBA')
        # convert to grayscale
        img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
        # blur the image for better edge detection
        img_blur = cv2.GaussianBlur(img_gray, (int(gaussian_blur), int(gaussian_blur)), 0)

        edges = cv2.Canny(img_blur, float(high_threshold), float(low_threshold))

        if draw_graphs:
            im = Image.fromarray(edges).convert(mode='RGBA')
            buf = io.BytesIO()
            im.save(buf, format='PNG')

            buf.seek(0)
            image = (base64.b64encode(buf.getvalue()).decode('ascii'))

            buf.close()

            name = 'Image'
            if expected_frame_count > 1:
                name = 'Frame ' + str(frame_count)

            graphs.append({
                'name': name,
                'image': image,
                'imageMimeType': 'image/png',
                'type': 'image'
            })

        all_features = all_features + [ float(x / 255) for x in edges.flatten().tolist() ]

    return {
        'features': [ int(x) for x in all_features ],
        'graphs': graphs,
        'output_config': {
            # type can be 'flat', 'image' or 'spectrogram'
            'type': 'image',
            'shape': {
                # shape should be { width, height, channels } for image, { width, height } for spectrogram
                'width': int(width),
                'height': int(height),
                'channels': 1
            }
        }
    }
