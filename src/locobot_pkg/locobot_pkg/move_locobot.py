import rclpy 
from rclpy.node import Node 
from rclpy.action import ActionClient

from irobot_create_msgs.action import Undock
from irobot_create_msgs.msg import DockStatus

from geometry_msgs.msg import Point, Quaternion
from geometry_msgs.msg import Twist

from locobot_pkg.go_to_position import GoToPosition

from time import sleep


class MoveLocobot(Node): 

    def __init__(self): 
        super().__init__("move_locobot")
        self.get_logger().info("MoveLocobot Node has been started")
        self.isDocked = True

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.undock_status_verifier = self.create_subscription(DockStatus, '/dock_status', self.parseDockStatusVerifier, 10)
        
        self.action_undocker_ = ActionClient(self, Undock, '/undock')
        self.undock()

    def moveRobot(self): 

        cmd = Twist()
        cmd.linear.x = 0.5 
        cmd.angular.z = 0.1 

        self.publisher_.publish(cmd)
    
    def undock(self):
        # Créer l'objectif pour l'undocking
        goal_msg = Undock.Goal()
        
        # Envoyer l'objectif à l'action /undock
        self.get_logger().info('Envoi de la demande d\'undocking...')
        self.action_undocker_.wait_for_server()
        future = self.action_undocker_.send_goal_async(goal_msg)
        
        # Attendre la réponse
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):

        # Callback quand le résultat de l'undock est reçu
        result = future.result()
        if result:
            if self.isDocked==False:  
                self.get_logger().info(f"Undocking terminé avec succès. Status: {result.status}") 

                goToPos = GoToPosition(self)
                goToPos.navigate(self.whenNavigateToPoseIsDone, Point(x=-5.0,y=0.0,z=0.0), Quaternion(x=0.0,y=0.0,z=0.0,w=1.0))
                # self.timer_ = self.create_timer(1/20, self.moveRobot)
            else: 
                sleep(3)
                self.goal_response_callback(future) 
            
        else:
            self.get_logger().error("Échec de l'undocking.")

    def whenNavigateToPoseIsDone(self, result): 
        self.get_logger().info("Position is reached")

    def parseDockStatusVerifier(self, result):
        self.get_logger().info(f"New dock position {result.is_docked}")

        self.isDocked  = result.is_docked 

def main(args = None): 
    rclpy.init(args=args)
    node = MoveLocobot()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__": 
    main()
