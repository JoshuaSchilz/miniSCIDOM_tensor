"""Check if spatial resolution s is put in correctly"""
ROI_diam = 2.5  # Diameter for the evaluated Region in mm (mask)
ROI_diam_sum = 2.5  # Diameter for the evaluated summed up Region (mask)
max_err = 0.05  # Reconstruction stops if relative Error is lower than this value
max_it = 4  # Maximum number of Iterations if Error threshold is not achieved
# it tends to get worse after the 4th or 5th iteration

if facility == "2" and shooting_date == "1":
    shape_front = (170, 130)  # you can not reconstruct somethin bigger than 190
    shape_side = (140, 130)

    deltaz = 140  # proton measurements
    rot_angle = 89.9

    x_0 = int(0)
    y_0 = int(-5)

    y1_front = y_0 + 451
    y2_front = y_0 + 621
    x1_front = x_0 + 458
    x2_front = x_0 + 588

    y1_top = y_0 + 655
    y2_top = y_0 + 795
    x1_top = x_0 + 459
    x2_top = x_0 + 589

    y1_120 = y_0 + 650
    y2_120 = y_0 + 790
    x1_120 = x_0 + 267
    x2_120 = x_0 + 397

    y1_240 = y_0 + 650
    y2_240 = y_0 + 790
    x1_240 = x_0 + 649
    x2_240 = x_0 + 779

    ###shift
    shift_image_front = [0, 0]
    shift_image_top = [0, 0]
    shift_image_120 = [8, 0]
    shift_image_240 = [-8, 0]

#%% PB
if facility == "2" and shooting_date == "2":
    shape_front = (150, 105)  # you can not reconstruct somethin bigger than 190
    shape_side = (140, 105)

    deltaz = 140  # proton measurements
    rot_angle = -0.1

    x_0 = int(175)
    y_0 = int(0)

    y1_front = y_0 + 270
    y2_front = y1_front + shape_front[0]
    x1_front = x_0 + 470
    x2_front = x1_front + shape_front[1]

    y1_top = y_0 + 474
    y2_top = y1_top + shape_side[0]
    x1_top = x_0 + 470
    x2_top = x1_top + shape_side[1]

    y1_120 = y_0 + 476
    y2_120 = y1_120 + shape_side[0]
    x1_120 = x_0 + 275
    x2_120 = x1_120 + shape_side[1]

    y1_240 = y_0 + 476
    y2_240 = y1_240 + shape_side[0]
    x1_240 = x_0 + 667
    x2_240 = x1_240 + shape_side[1]

    ###shift
    shift_image_front = [0, 0]
    shift_image_top = [0, 0]
    shift_image_120 = [0, 0]
    shift_image_240 = [0, 0]

#%% Draco
if facility == "1":
    shape_front = (186, 135)  # you can not reconstruct somethin bigger than 190
    shape_side = (159, 135)

    deltaz = 159  # proton measurements
    rot_angle = -0.1

    x_0 = int(-128)
    y_0 = int(709)

    y1_front = y_0 + -250
    y2_front = y1_front + shape_front[0]
    x1_front = x_0 + 529
    x2_front = x1_front + shape_front[1]

    y1_top = y_0 + -2
    y2_top = y1_top + shape_side[0]
    x1_top = x_0 + 531
    x2_top = x1_top + shape_side[1]

    y1_120 = y_0 + 0
    y2_120 = y1_120 + shape_side[0]
    x1_120 = x_0 + 285
    x2_120 = x1_120 + shape_side[1]

    y1_240 = y_0 + 0
    y2_240 = y1_240 + shape_side[0]
    x1_240 = x_0 + 770
    x2_240 = x1_240 + shape_side[1]

    ###shift
    shift_image_front = [0, 0]
    shift_image_top = [0, 0]
    shift_image_120 = [0, 0]
    shift_image_240 = [0, 0]

#%% Online
if facility == "4":
    shape_front = (150, 110)
    shape_side = (310, 110)
    deltaz = 310
    rot_angle = 0
    x_0 = 5
    y_0 = 0
    y1_front = 195
    y2_front = 345
    x1_front = 633
    x2_front = 743
    y1_top = 447
    y2_top = 757
    x1_top = 633
    x2_top = 743
    y1_120 = 442
    y2_120 = 752
    x1_120 = 902
    x2_120 = 1012
    y1_240 = 442
    y2_240 = 752
    x1_240 = 374
    x2_240 = 484

    ###shift
    shift_image_front = [0, 0]
    shift_image_top = [0, 0]
    shift_image_120 = [0, 0]
    shift_image_240 = [0, 0]