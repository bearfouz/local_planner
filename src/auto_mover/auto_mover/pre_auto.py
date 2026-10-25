# improvements to be made
# When rover doesn't get current_x, i.e., when odometry isn't published

# multiple waypoint iteration

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import numpy as np

class pre_auto(Node):
    def __init__(self,):
        
        super().__init__("pre_auto")
        
        # parameters
        self.declare_parameter("forward_vel", 0.0)
        self.declare_parameter("yaw_vel", 0.0)

        # multiple waypoint
        self.declare_parameter("target_x0", 0.0)
        self.declare_parameter("target_y0", 0.0)
        self.declare_parameter("target_x1", 0.0)
        self.declare_parameter("target_y1", 0.0)
        self.declare_parameter("target_x2", 0.0)
        self.declare_parameter("target_y2", 0.0)
        self.declare_parameter("target_x3", 0.0)
        self.declare_parameter("target_y3", 0.0)


        self.declare_parameter("dist_threshold", 0.0)
        self.declare_parameter("yaw_threshold", 0.0)

        #timer
        self.timer = self.create_timer(0.3, self.main_callback)

        # publishers
        self.move = self.create_publisher(Twist, "/cmd_vel", 1) # check if fps synced
        self.current_pose = self.create_subscription(Odometry, "/okvis/okvis_odometry", self.pose_callback, 1)

        # all variables

        self.thresh_d = self.get_parameter("dist_threshold").value
        self.thresh_y = self.get_parameter("yaw_threshold").value

        # Waypoints
        self.target_x0 = self.get_parameter("target_x0").value
        self.target_y0 = self.get_parameter("target_y0").value
        self.target_x1 = self.get_parameter("target_x1").value
        self.target_y1 = self.get_parameter("target_y1").value
        self.target_x2 = self.get_parameter("target_x2").value
        self.target_y2 = self.get_parameter("target_y2").value
        self.target_x3 = self.get_parameter("target_x3").value
        self.target_y3 = self.get_parameter("target_y3").value

        self.waypoints = [(self.target_x0, self.target_y0), (self.target_x1, self.target_y1), (self.target_x2, self.target_y2), (self.target_x3, self.target_y3)]

        # movement
        self.forward = Twist()
        self.left = Twist()
        self.right = Twist()
        self.stop = Twist()

        self.forward.linear.x = self.get_parameter("forward_vel").value
        self.left.angular.z = -self.get_parameter("yaw_vel").value
        self.right.angular.z = self.get_parameter("yaw_vel").value
        self.stop.linear.x = 0.0
        self.stop.angular.z = 0.0

        self.get_logger().info("Node started!")

        self.iter = 0
        self.final_reached = False

    def pose_callback(self, msg: Odometry):
        # pose
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.current_yaw = np.degrees(math.atan2(2*(msg.pose.pose.orientation.w*msg.pose.pose.orientation.z + msg.pose.pose.orientation.x*msg.pose.pose.orientation.y), 1 - 2*(msg.pose.pose.orientation.y*msg.pose.pose.orientation.y + msg.pose.pose.orientation.z*msg.pose.pose.orientation.z)))

    def distance(self, t_x, c_x, t_y, c_y):
        dist = math.sqrt((t_x - c_x) ** 2 + (t_y - c_y) ** 2)
        return dist

    def orient(self, t_y, c_y, t_x, c_x):
        angle = np.degrees(np.arctan2(t_y - c_y, t_x - c_x))
        return angle

    def main_callback(self):

        if self.iter == 4:
            self.final_reached = True
        
        if not self.final_reached:
    
            # stop condition
            target_x = self.waypoints[self.iter][0]
            target_y = self.waypoints[self.iter][1]

            if self.distance(target_x, self.current_x, target_y, self.current_y) < self.thresh_d:
                msg = self.stop
                self.get_logger().info(f"Goal {self.iter + 1} Reached!")
                self.iter += 1

            else:        
                # forward logic
                upper_limit = self.orient(target_y, self.current_y, target_x, self.current_x) + self.thresh_y
                lower_limit = self.orient(target_y, self.current_y, target_x, self.current_x) - self.thresh_y

                if lower_limit < self.current_yaw + 90 < upper_limit:
                    self.get_logger().info("Moving Forward!")
                    msg = self.forward
                elif self.current_yaw + 90 > upper_limit:
                    self.get_logger().info("Moving right!")
                    msg = self.right
                else:
                    self.get_logger().info("Moving left!")
                    msg = self.left         

            self.move.publish(msg)

def main():
    rclpy.init()

    auto = pre_auto()

    rclpy.spin(auto)

    auto.destroy_node()

    rclpy.shutdown()

if __name__ == "__main__":
    main()