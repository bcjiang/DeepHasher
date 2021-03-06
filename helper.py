# Helper function definitinos
import numpy as np
from math import hypot, atan2, cos, sin

def randRot3():
    """Generate a 3D random rotation matrix.
    Returns:
        np.matrix: A 3D rotation matrix.
    """
    x1, x2, x3 = np.random.rand(3)
    R = np.matrix([[np.cos(2 * np.pi * x1), np.sin(2 * np.pi * x1), 0],
                   [-np.sin(2 * np.pi * x1), np.cos(2 * np.pi * x1), 0],
                   [0, 0, 1]])
    v = np.matrix([[np.cos(2 * np.pi * x2) * np.sqrt(x3)],
                   [np.sin(2 * np.pi * x2) * np.sqrt(x3)],
                   [np.sqrt(1 - x3)]])
    H = np.eye(3) - 2 * v * v.T
    M = -H * R
    return M


def randTrans4x4(dataset='pancreas',debug=False):
    """
    Generate random 4x4 transformation
    """
    F = np.diag([1, 1, 1, 1])
    if debug:
        return F
    else:
        if dataset == 'pancreas':
            F[0:3, 0:3] = randRot3()
            F[2, 3] = np.random.rand(1) * (-239.0)
            F[3, 3] = 1.0
        elif dataset == 'liver':
            F[0:3, 0:3] = randRot3()
            F[2, 3] = np.random.rand(1) * 254 - 87.76
            F[3, 3] = 1.0
        return F


def compute_error(gt, re):
    # gt for ground truth, re for prediction result
    gtba = gt[:, 0:3] - gt[:, 3:6]
    gtbc = gt[:, 6:9] - gt[:, 3:6]
    gtnormal = np.cross(gtba, gtbc)
    gtnormal = gtnormal / ((np.linalg.norm(gtnormal, axis=-1))[:, None])
    gtcenter = (gt[:, 0:3] + gt[:, 3:6] + gt[:, 6:9]) / ((np.ones([gt.shape[0]]) * 3)[:, None])

    reba = re[:, 0:3] - re[:, 3:6]
    rebc = re[:, 6:9] - re[:, 3:6]
    renormal = np.cross(reba, rebc)
    renormal = renormal / ((np.linalg.norm(renormal, axis=-1))[:, None])
    recenter = (re[:, 0:3] + re[:, 3:6] + re[:, 6:9]) / ((np.ones([re.shape[0]]) * 3)[:, None])

    dotnormal = [np.degrees(np.arccos(np.dot(gtnormal[i, :], renormal[i, :]))) for i in range(gtnormal.shape[0])]
    diff_normal_avg = np.array(dotnormal).mean()

    diff_center = gtcenter - recenter
    diff_center = np.linalg.norm(diff_center, axis=-1)
    diff_center_avg = diff_center.mean()

    return diff_center_avg, diff_normal_avg


def compute_error_geom(y, y_pred):
    # y for ground truth, y_pred for prediction result
    diff_normal = 0.0
    for i in range(y.shape[0]):
        Ry = axang2rotm(y[i, :3])
        Ry_pred = axang2rotm(y_pred[i, :3])
        R_diff = np.matmul(Ry, np.transpose(Ry_pred))
        w_diff = rotm2axang(R_diff)
        diff_normal += np.linalg.norm(w_diff)*180/np.pi
    diff_normal_avg = diff_normal / y.shape[0]

    diff_center = y[:,3:6] - y_pred[:,3:6]
    diff_center = np.linalg.norm(diff_center, axis=-1)
    diff_center_avg = diff_center.mean()

    return diff_center_avg, diff_normal_avg


def rotm2axang(R):
    """
    Convert the rotation matrix into the axis-angle notation.
    """
    axis = np.zeros(3)
    axis[0] = R[2, 1] - R[1, 2]
    axis[1] = R[0, 2] - R[2, 0]
    axis[2] = R[1, 0] - R[0, 1]

    r = hypot(axis[0], hypot(axis[1], axis[2]))
    t = R[0, 0] + R[1, 1] + R[2, 2]
    theta = atan2(r, t - 1)

    if r != 0.0:
        axis = axis / r

    w = axis * theta

    return w


def axang2rotm(w):
    angle = np.linalg.norm(w)
    axis = w / angle

    R = np.zeros([3, 3])

    # Trig factors
    ca = cos(angle)
    sa = sin(angle)
    C = 1 - ca

    # Depack the axis
    x, y, z = axis

    # Multiplications (to remove duplicate calculations)
    xs = x * sa
    ys = y * sa
    zs = z * sa
    xC = x * C
    yC = y * C
    zC = z * C
    xyC = x * yC
    yzC = y * zC
    zxC = z * xC

    # Update the rotation matrix.
    R[0, 0] = x * xC + ca
    R[0, 1] = xyC - zs
    R[0, 2] = zxC + ys
    R[1, 0] = xyC + zs
    R[1, 1] = y * yC + ca
    R[1, 2] = yzC - xs
    R[2, 0] = zxC - ys
    R[2, 1] = yzC + xs
    R[2, 2] = z * zC + ca

    return R