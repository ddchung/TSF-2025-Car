import lane_follower
from ultralytics import YOLO
import lane_follower
import cv2

image = cv2.imread("./test2.jpg")

lane_lines = lane_follower.detect_lane(image)
image = lane_follower.display_lines(image, lane_lines)

height, width = image.shape[:2]
print(f"WIDTH & HEIGHT: {width}, {height}")
road = lane_follower.road_area(lane_lines, width, height)

if len(road) > 0:
    #coordinate = (300, 500)
    res = True
    image = lane_follower.draw_road(image, road, True)
    if res:
        pass
        #ew_task = multiprocessing.Thread(target=adapter.stop_move)

cv2.imshow("Traffic sign detector", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

