import cv2
import numpy as np

def LaneROI(frame,mask,minArea):
    
   
    Lane_gray_opened = mask
    Lane_gray_Smoothed = cv2.GaussianBlur(mask,(11,11),1) # Smoothing out the edges for edge extraction later

    # 4d. Keeping only Edges of Segmented ROI    
    Lane_edge = cv2.Canny(Lane_gray_Smoothed,50,150, None, 3) # Extracting the Edge of Canny


    return Lane_edge,Lane_gray_opened

def prep_ROIs(frame):
    height, width = frame.shape

    masked_image = frame

    ## Choosing points for Center ROI
    bl = (width//4, height)
    tl = (width//2-50, height//2+10)
    tr = (width//2+50, height//2+10)
    br = (width//5*4, height)
    mask = np.zeros_like(masked_image)
    ROI = np.array([[bl,tl,tr,br]], np.int32)
    cv2.fillPoly(mask, ROI, (255,255,255))
    # cv2.imshow('ROI_Center_mask',mask)
    ROI_center = cv2.bitwise_and(masked_image, mask)
    # cv2.imshow('ROI_mid',ROI_center)

    ## Choosing points for Mid ROI
    bl = (0 ,height)
    tl = (0, 0)
    tr = (width//2, 0)
    br = (width//2,height)
    mask = np.zeros_like(masked_image)
    ROI = np.array([[bl,tl,tr,br]], np.int32)
    cv2.fillPoly(mask, ROI, (255,255,255))
    # cv2.imshow('ROI_mask',mask)
    ROI_img = cv2.bitwise_and(masked_image, mask)
    # cv2.imshow('ROI_mid',ROI_img)

    ## Choosing points for Outer ROI
    bl = (width//2,height)
    tl = (width//2, 0)
    tr = (width,0)
    br = (width,height)
    mask = np.zeros_like(masked_image)
    ROI = np.array([[bl,tl,tr,br]], np.int32)
    cv2.fillPoly(mask, ROI, (255,255,255))
    # cv2.imshow('ROI_mask_Y',mask)
    ROI_img_Y = cv2.bitwise_and(masked_image, mask)
    # cv2.imshow('ROI_out',ROI_img_Y)

    return ROI_img, ROI_img_Y, ROI_center

def canny(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = 7
    blur = cv2.GaussianBlur(gray,(kernel, kernel),0)
    canny = cv2.Canny(blur, 50, 150)
    return canny

def draw_white_line(image,side):
    # Get the height and width of the image
    height, width = image.shape

    # Create a copy of the image to draw the line on
    result_image = np.copy(image)

    # Define the starting and ending points of the line
    # if (side == 'L'):
    #     start_point = (width//2-165, height // 2 + 100)
    #     end_point = (width//2-165, height)
    # elif (side == 'R'):
    #     start_point = (width//2+165, height // 2 +100)
    #     end_point = (width//2+165, height)

    off_set = 90
    if (side == 'L'):
        start_point = (off_set, height // 2 + 100)
        end_point = (off_set, height)
    elif (side == 'R'):
        start_point = (width-off_set, height // 2 +100)
        end_point = (width-off_set, height)

    # Draw a white line on the image
    result_image = cv2.line(result_image, start_point, end_point, 255, thickness=20)

    return result_image


def find_top_bottom_points(image):

    # Tìm tất cả các contours trong ảnh
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Kiểm tra nếu không có contour nào được tìm thấy
    if not contours:
        return None, None

    # Tìm contour trên cùng và dưới cùng
    topmost = tuple(contours[0][contours[0][:, :, 1].argmin()][0])
    bottommost = tuple(contours[0][contours[0][:, :, 1].argmax()][0])

    return topmost, bottommost

def draw_white_line_with_ref(image,ref_img):
    # Get the height and width of the image
    height, width = image.shape

    _, end_point = find_top_bottom_points(ref_img)
    # if end_point[0] > width//2:

    start_point = (width - end_point[0],height // 2 + 100)

    # Draw a white line on the image
    result_image = cv2.line(result_image, start_point, end_point, 255, thickness=20)

    return result_image


def remove_horizontal_lines(image,theta_thresh):
    
    _, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Find lines
    lines = cv2.HoughLines(binary_image, 1, np.pi/180, threshold=100)

    # clear all horizontal lines
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            if ((theta >= (np.pi/2-theta_thresh)) and (theta <= (np.pi/2+theta_thresh))):  # check if horizontal line
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0), 5)

    return image

def Zebra_Processing(image):
    Zebra_cross = False
    height, width = image.shape
    
    lines = cv2.HoughLines(image, 1, np.pi/180, threshold=20)

    leftmost_line = None
    rightmost_line = None
    slash_lines = []        # Danh sách lưu các đường //
    backslash_lines = []    # Danh sach luu cac duong \\

    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            # print(f"1.theta = {theta}\n")
            if abs(theta - np.pi / 4) < np.pi/10:
                # print(f"2.theta = {theta}\n")
                slash_lines.append(line[0])  # Lưu các đường thẳng //
            elif  abs(theta - 3 * np.pi / 4) < np.pi / 10:
                backslash_lines.append(line[0])  # Lưu các đường thẳng \\


    # Sắp xếp danh sách các đường thẳng dựa trên giá trị của rho
    slash_lines.sort(key=lambda x: x[0])
    backslash_lines.sort(key=lambda x: x[0])

    # Lấy đường nằm bên trái cùng và bên phải cùng
    if slash_lines:
        # Sắp xếp danh sách các đường thẳng dựa trên giá trị của rho
        slash_lines.sort(key=lambda x: x[0])
        leftmost_line = slash_lines[0]
    if backslash_lines:
        backslash_lines.sort(key=lambda x: x[0])
        rightmost_line = backslash_lines[-1]

    zebra_result_img = np.zeros_like(image)
    # print(f"left_most_line = {leftmost_line}")
    # Vẽ hai đường `leftmost` và `rightmost` bằng màu trắng và độ dày 10
    if leftmost_line is not None and rightmost_line is not None:
        
        # print("===        Both LEFT and RIGHT MOST            ===")
        rho_left, theta_left = leftmost_line
        rho_right, theta_right = rightmost_line

        a_left = np.cos(theta_left)
        b_left = np.sin(theta_left)
        x0_left = a_left * rho_left
        y0_left = b_left * rho_left
        x1_left = int(x0_left + 1000 * (-b_left))
        y1_left = int(y0_left + 1000 * (a_left))
        x2_left = int(x0_left - 1000 * (-b_left))
        y2_left = int(y0_left - 1000 * (a_left))

        a_right = np.cos(theta_right)
        b_right = np.sin(theta_right)
        x0_right = a_right * rho_right
        y0_right = b_right * rho_right
        x1_right = int(x0_right + 1000 * (-b_right))
        y1_right = int(y0_right + 1000 * (a_right))
        x2_right = int(x0_right - 1000 * (-b_right))
        y2_right = int(y0_right - 1000 * (a_right))
        
        cv2.line(zebra_result_img, (x1_left, y1_left), (x2_left, y2_left), (255, 255, 255), 10)
        cv2.line(zebra_result_img, (x1_right, y1_right), (x2_right, y2_right), (255, 255, 255), 10)


        ## Choosing points for LANE-only ROI
        height, width = zebra_result_img.shape
        bl = (0 ,height)
        ml = (0, height//2 + 120 )
        tl = (50, height//2 + 80)
        tr = (width-50, height//2 + 80)
        mr = (width, height//2 + 120)
        br = (width,height)
        mask = np.zeros_like(zebra_result_img)
        ROI = np.array([[bl,ml,tl,tr,mr,br]], np.int32)
        cv2.fillPoly(mask, ROI, (255,255,255))
        zebra_result_img = cv2.bitwise_and(zebra_result_img, mask)


        #Tim 4 diem tao mask ==> xet Zebra_crossing flag
        zebra_left, zebra_right, _ = prep_ROIs(zebra_result_img)
        top_left, bot_left = find_top_bottom_points(zebra_left)
        top_right, bot_right = find_top_bottom_points(zebra_right)
        
        
        if None not in (top_left, bot_left, top_right, bot_right):
            if top_left[0] < width//2-10 and bot_left[0] < width//2-10 and top_right[0] > width//2-10 and bot_right[0] > width//2-10:
                
                # Chose Zebra Zone
                bl = (bot_left[0]+30,bot_left[1])
                tl = (top_left[0]+30,top_left[1])
                tr = (top_right[0]-30,top_right[1])
                br = (bot_right[0]-30,bot_right[1])
                Zebra_zone_mask = np.zeros_like(image)
                ROI = np.array([[bl,tl,tr,br]], np.int32)
                cv2.fillPoly(Zebra_zone_mask, ROI, (255,255,255))
                # cv2.imshow('Zebra_zone_mask',Zebra_zone_mask)
                Zebra_zone = cv2.bitwise_and(image, Zebra_zone_mask)
                # cv2.imshow('Zebra_zone',Zebra_zone)


                lines = cv2.HoughLines(Zebra_zone, 1, np.pi/180, threshold=20)
                valid_lines = []  # Danh sách lưu các đường thẳng thỏa điều kiện / hoac \
                if lines is not None:
                    count = 0
                    for line in lines:
                        rho, theta = line[0]
                        if (abs(theta - np.pi / 4) < np.pi / 3 or abs(theta - 3 * np.pi / 4) < np.pi / 3):
                            count += 1
                            valid_lines.append(line[0])  # Lưu các đường thẳng thỏa điều kiện

                    if count > 20:
                        Zebra_cross = True
    elif leftmost_line is not None and rightmost_line is None:
        # print("===        Only_LEFT MOST            ===")
        zebra_result_img = image.copy()
        rho_left, theta_left = leftmost_line
        a_left = np.cos(theta_left)
        b_left = np.sin(theta_left)
        x0_left = a_left * rho_left
        y0_left = b_left * rho_left
        x1_left = int(x0_left + 1000 * (-b_left))
        y1_left = int(y0_left + 1000 * (a_left))
        x2_left = int(x0_left - 1000 * (-b_left))
        y2_left = int(y0_left - 1000 * (a_left))
        cv2.line(zebra_result_img, (x1_left, y1_left), (x2_left, y2_left), (255, 255, 255), 10)
        
        ## Choosing points for LANE-only ROI
        height, width = zebra_result_img.shape
        bl = (0 ,height)
        ml = (0, height//2 + 120 )
        tl = (50, height//2 + 80)
        tr = (width-50, height//2 + 80)
        mr = (width, height//2 + 120)
        br = (width,height)
        mask = np.zeros_like(zebra_result_img)
        ROI = np.array([[bl,ml,tl,tr,mr,br]], np.int32)
        cv2.fillPoly(mask, ROI, (255,255,255))
        zebra_result_img = cv2.bitwise_and(zebra_result_img, mask)
    elif leftmost_line is None and rightmost_line is not None:
        zebra_result_img = image.copy()
        # print("===        Only_RIGHT MOST            ===")
        rho_right, theta_right = rightmost_line
        a_right = np.cos(theta_right)
        b_right = np.sin(theta_right)
        x0_right = a_right * rho_right
        y0_right = b_right * rho_right
        x1_right = int(x0_right + 1000 * (-b_right))
        y1_right = int(y0_right + 1000 * (a_right))
        x2_right = int(x0_right - 1000 * (-b_right))
        y2_right = int(y0_right - 1000 * (a_right))
        cv2.line(zebra_result_img, (x1_right, y1_right), (x2_right, y2_right), (255, 255, 255), 10)
        
        ## Choosing points for LANE-only ROI
        height, width = zebra_result_img.shape
        bl = (0 ,height)
        ml = (0, height//2 + 120 )
        tl = (50, height//2 + 80)
        tr = (width-50, height//2 + 80)
        mr = (width, height//2 + 120)
        br = (width,height)
        mask = np.zeros_like(zebra_result_img)
        ROI = np.array([[bl,ml,tl,tr,mr,br]], np.int32)
        cv2.fillPoly(mask, ROI, (255,255,255))
        zebra_result_img = cv2.bitwise_and(zebra_result_img, mask)
    else:
        zebra_result_img = image

    return zebra_result_img, Zebra_cross

def shift_image(image, direction, shift_amount):
    # Get the height and width of the image
    height, width = image.shape

    if (direction == 'R'):
        # Create a matrix to shift the image to the right
        M = np.float32([[1, 0, shift_amount], [0, 1, 0]])
    elif (direction == 'L'):
        # Create a matrix to shift the image to the left
        M = np.float32([[1, 0, -shift_amount], [0, 1, 0]])

    # Use the warpAffine function to apply the shift
    shifted_image = cv2.warpAffine(image, M, (width, height))

    return shifted_image

def Segment(frame):
    """ Segment Lane-Lines (both outer and middle) from the road lane
    """

    src = frame.copy()
    
    src = canny(src)

    src = remove_horizontal_lines(src,theta_thresh = 0.15)
    # cv2.imwrite("frame_wo_horizonetal_lines.png",src)
    
    ## Choosing points for LANE-only ROI
    height, width = src.shape
    bl = (0 ,height)

    # ml = (0, height//2 + 170 )
    # tl = (100, height//2 + 80)
    # tr = (width-100, height//2 + 80)
    # mr = (width, height//2 + 170)

    ml = (0, height//2 + 150 )
    tl = (0, height//2 + 110)
    tr = (width, height//2 + 110)
    mr = (width, height//2 + 150)
    
    br = (width,height)
    mask = np.zeros_like(src)
    ROI = np.array([[bl,ml,tl,tr,mr,br]], np.int32)
    cv2.fillPoly(mask, ROI, (255,255,255))
    src = cv2.bitwise_and(src, mask)
    # cv2.imwrite('LANE-only_area.png',mask)

    # Detect Zebra_crossing mark and erase them if exist
    src, Zebra_cross = Zebra_Processing(src)
    # cv2.imwrite("Zebra_result.png",src)
    

    # Define a kernel (structuring element) for dilation/erosion
    # kernel = np.ones((20, 20), np.uint8)  
    # src = cv2.dilate(src, kernel, iterations=1)
    # kernel = np.ones((30, 30), np.uint8) 
    # src = cv2.erode(src, kernel, iterations=1)
    # cv2.imshow("SRC after dilate-erode", src)

    mask, mask_Y, mask_center = prep_ROIs(src)

    # cv2.imshow("mask_L",mask)
    # cv2.imshow("mask_R",mask_Y)

    Intersection_status = "False"

    # Create virtual line if less than 2 lines detected and Intersection check
    # 1. No line detected => Draw 2 virtual lines 
    # Intersection 4 : No blocking left or right
    if ((cv2.countNonZero(mask)<20) and (cv2.countNonZero(mask_Y)<20)):
        mask = draw_white_line(mask, 'L')
        mask_Y = draw_white_line(mask_Y, 'R')
        Intersection_status = "4 - No blocked"

    # # 2. One of 2 lines detected on 1 side 
    # #    => Create the other line by flipping the detected line
    # if ((cv2.countNonZero(mask_center)<20)):
    #     # Intersection 3 : Right blocked
    #     if ((cv2.countNonZero(mask)<20) and (cv2.countNonZero(mask_Y)>20)):
    #         mask = cv2.bitwise_or(mask, cv2.flip(mask_Y,1))
    #         if not Zebra_cross:
    #             Intersection_status = "3 - Right blocked"
    #     # Intersection 3 : Left blocked
    #     elif ((cv2.countNonZero(mask)>20) and (cv2.countNonZero(mask_Y)<20)):
    #         mask_Y = cv2.bitwise_or(mask_Y, cv2.flip(mask,1))
    #         if not Zebra_cross:
    #             Intersection_status = "3 - Left blocked"
    # # 3. One line detected in mask_center - Curved road
    # else:
    #     # 3.1. The detected line entirely in RIGHT side
    if ((cv2.countNonZero(mask)<20) and (cv2.countNonZero(mask_Y)>20)):
        # mask = draw_white_line_with_ref(mask,mask_Y)
        top_right,bot_right = find_top_bottom_points(mask_Y)
        if abs(bot_right[0] - width)<3:
            start_point = (0,top_right[1])
            end_point = (0,bot_right[1])
            mask = cv2.line(mask, start_point, end_point, 255, thickness=10)
        else:
            mask = shift_image(mask_Y, 'L', 2*abs(bot_right[0]-width//2))
            top_left,_= find_top_bottom_points(mask)
            start_point = (0,top_right[1])
            end_point = (0,top_left[1])
            mask = cv2.line(mask, start_point, end_point, 255, thickness=10)
    # 3.2. The detected line entirely in LEFT side
    elif ((cv2.countNonZero(mask)>20) and (cv2.countNonZero(mask_Y)<20)):
        # mask_Y = draw_white_line_with_ref(mask_Y, mask)
        top_left,bot_left = find_top_bottom_points(mask)
        if abs(bot_left[0])<3:
            start_point = (width,top_left[1])
            end_point = (width,bot_left[1])
            mask_Y = cv2.line(mask_Y, start_point, end_point, 255, thickness=10)
        else:
            mask_Y = shift_image(mask, 'R', 2*abs(bot_left[0]-width//2))
            top_right,_= find_top_bottom_points(mask_Y)
            start_point = (width,top_right[1])
            end_point = (width,top_left[1])
            mask_Y = cv2.line(mask_Y, start_point, end_point, 255, thickness=10)
    #     """
    #         SHIFT detected line instead of FLIP
    #     """
    #     # 3.3. The detected line is on BOTH sides => Handled by later process

   
    
    
    # Outer_edge_ROI,OuterLane_SidesSeperated,Outer_Points_list = OuterLaneROI(frame,mask_Y,20)#27msec

    Mid_edge_ROI,Mid_ROI_mask = LaneROI(frame,mask,minArea=20)#20 msec
    Out_edge_ROI,Out_ROI_mask = LaneROI(frame,mask_Y,minArea=20)
 
    return Mid_edge_ROI,Mid_ROI_mask,Out_edge_ROI,Out_ROI_mask,Zebra_cross,Intersection_status