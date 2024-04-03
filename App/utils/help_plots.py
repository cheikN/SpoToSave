import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn.preprocessing import StandardScaler

emotions_name_angle = {
    "activation" : 0.0,
    "alert" : 18.0,
    "excited" : 36.0,
    "elated" : 54.0,
    "happy" : 72.0,
    "pleasant" : 90.0,
    "contented" : 108.0,
    "serene" : 126.0,
    "relaxed" : 144.0,
    "calm" : 162.0,
    "dactivation/sleepy" : 180.0,
    "bored" : 198.0,
    "lethargic" : 216.0,
    "depressed" : 234.0,
    "sad" : 252.0,
    "unpleasant" : 270.0,
    "upset" : 288.0,
    "stressed" : 306.0,
    "nervous" : 324.0,
    "tense" : 342.0,
}


emotions_stats = {
    "activation" : [],
    "alert" : [],
    "excited" : [],
    "elated" : [],
    "happy" : [],
    "pleasant" : [],
    "contented" : [],
    "serene" : [],
    "relaxed" : [],
    "calm" : [],
    "dactivation/sleepy" : [],
    "bored" : [],
    "lethargic" : [],
    "depressed" : [],
    "sad" : [],
    "unpleasant" : [],
    "upset" : [],
    "stressed" : [],
    "nervous" : [],
    "tense" : [],
}


def get_emo_fromValEner(valence,energy):
    pt_udt = [valence,energy]
    pt_udt = create_vector(pt_udt,[0.5,0.5])
    pred_angle_upd = angle_between_vectors(pt_udt)
    emo = closest_value(emotions_name_angle,pred_angle_upd)[0]
    return emo

def angle_between_vectors(v2):
  """
  Calculates the angle between two vectors in degrees (0-360).

  Args:
      v1: A numpy array representing the first vector.
      v2: A numpy array representing the second vector.

  Returns:
      The angle between the two vectors in degrees (0-360).
  """
  v1 = [0,1]
  # Calculate the dot product
  dot_product = np.dot(v1, v2)

  # Calculate the magnitudes
  magnitude1 = np.linalg.norm(v1)
  magnitude2 = np.linalg.norm(v2)

  # Check for zero vectors (division by zero)
  if magnitude1 == 0 or magnitude2 == 0:
    return 0

  # Use arctan2 to handle angles in all quadrants
  angle_rad = np.arctan2(v1[1], v1[0]) - np.arctan2(v2[1], v2[0])

  # Convert to degrees and ensure the angle is between 0 and 360
  angle_deg = np.degrees(angle_rad) % 360.0

  return angle_deg

def circle_points(r, n):
    circles = []
    for r, n in zip(r, n):
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        x = r * np.sin(t) + 0.5
        y = r * np.cos(t) + 0.5
        circles.append(np.c_[x, y])
    return circles

def closest_value(data,value):
    min_ecart = 999999999
    best_angle = -1
    best_emo = ""
    for emo,angle in data.items(): #ameliorable
        if abs(angle-value) < min_ecart:
            min_ecart = abs(angle-value)
            best_angle = angle
            best_emo = emo
    return best_emo,best_angle

def create_vector(point,origin):
    return([point[0] - origin[0], point[1] - origin[1]])

def plot_example_emo(ind, df):

    valence = df.loc[ind, "valence"]
    energy = df.loc[ind, "energy"]
    emo = df.loc[ind, "emo_russel"]
    
    pt_udt = [valence,energy]
    pt_udt = create_vector(pt_udt,[0.5,0.5])

    pred_angle_upd = angle_between_vectors(pt_udt)
    
    #print(closest_value(emotions_name_angle,pred_angle_upd))
    
    origin = np.array([[0.5],[0.5]]) # origin point
    emotions_name = list(emotions_name_angle.keys())

    circle10 = circle_points([0.5], [20])[0] # 10 points on a circle

    fig, ax = plt.subplots()
    plt.title(f'{df.loc[ind, "title"]} by {df.loc[ind, "artist"]} : [{emo}]')
    ax.scatter(circle10[:, 0], circle10[:, 1], color='crimson')
    ax.scatter(valence, energy)

    for i, (x, y) in enumerate(circle10):
        ax.text(x+0.05, y + 0.05, emotions_name[i], ha='center', va='center', color='crimson')
    
    ax.set_aspect('equal')
    ax.margins(x=0.1, y=0.1) # extra margins, because the text isn't taken into account for the default margins

    plt.quiver(0.5,0.5, 0,1, color=['b'],scale = 0.9, scale_units="inches")

    #plt.quiver(*origin, pt[0], pt[1], color=['r'],scale = 0.9, scale_units="inches")

    plt.quiver(*origin, pt_udt[0], pt_udt[1], color=['g'],scale = 0.9, scale_units="inches")
    
    ax.spines['left'].set_position('center')
    ax.spines['bottom'].set_position('center')

    # Eliminate upper and right axes
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    # Show ticks in the left and lower axes only
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    
    return  fig


def plot_radar(labels,cluster,fts,features):
    #fts = get_features_name()
    #features = st.session_state["data"].loc[labels == cluster,fts]

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    scaled_features = np.mean(scaled_features,axis=0)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="polar")

    # theta has 5 different angles, and the first one repeated
    theta = np.arange(len(scaled_features) + 1) / float(len(scaled_features)) * 2 * np.pi
    # values has the 5 values from 'Col B', with the first element repeated
    values = scaled_features
    values = np.append(values, values[0])
    # draw the polygon and the mark the points for each angle/value combination
    l1, = ax.plot(theta, values, color="C2", marker="o", label="Audio analyses")
    plt.xticks(theta[:-1], list(fts), color='grey', size=12)
    ax.tick_params(pad=10) # to increase the distance of the labels to the plot
    # fill the area of the polygon with green and some transparency
    ax.fill(theta, values, 'green', alpha=0.1)

    # plt.legend() # shows the legend, using the label of the line plot (useful when there is more than 1 polygon)
    return fig, features.mean()