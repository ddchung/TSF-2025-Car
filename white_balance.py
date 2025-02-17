# auto white balance

import numpy as np

def automatic_white_balance(image):
    """
    Performs automatic white balance correction using the Gray World Assumption.
    
    :param image: Input BGR image
    :return: White-balanced image
    """
    # Convert image to float for calculations
    result = image.astype(np.float32)

    # Compute mean values of each channel
    mean_b = np.mean(result[:, :, 0])
    mean_g = np.mean(result[:, :, 1])
    mean_r = np.mean(result[:, :, 2])

    # Compute scale factors
    avg_gray = (mean_b + mean_g + mean_r) / 3
    scale_b = avg_gray / mean_b
    scale_g = avg_gray / mean_g
    scale_r = avg_gray / mean_r

    # Apply scaling to each channel
    result[:, :, 0] = np.clip(result[:, :, 0] * scale_b, 0, 255)
    result[:, :, 1] = np.clip(result[:, :, 1] * scale_g, 0, 255)
    result[:, :, 2] = np.clip(result[:, :, 2] * scale_r, 0, 255)

    return result.astype(np.uint8)

if __name__ == "__main__":
    import cv2
    import frame_client

    while True:
        frame = frame_client.recv()
        if frame is None:
            break
        frame = automatic_white_balance(frame)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
