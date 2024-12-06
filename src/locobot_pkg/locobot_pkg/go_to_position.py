import rclpy
from rclpy.action import ActionClient
from irobot_create_msgs.action import NavigateToPosition


class GoToPosition:
    def __init__(self, node):
        """
        Initialisation de la classe GoToPosition.
        :param node: Le node ROS 2 auquel cette classe est attachée.
        """
        self.node = node
        # Créer un client d'action pour l'action /navigate_to_position
        self._action_client = ActionClient(self.node, NavigateToPosition, '/navigate_to_position')

    def navigate(self, callback, position, orientation):
        """
        Méthode pour envoyer un but de navigation.
        :param callback: Fonction à appeler lorsque l'action est terminée.
        """
        # Créer le message de goal (objectif) pour l'action NavigateToPosition
        goal_msg = NavigateToPosition.Goal()

        # Spécifier la position cible et l'orientation
        goal_msg.achieve_goal_heading = True

        # Définir la position cible avec des valeurs (x: 1.0, y: 0.2, z: 0.0)
        goal_msg.goal_pose.pose.position = position # Point(x=1.0, y=0.2, z=0.0)

        # Définir l'orientation avec une quaternion (orientation neutre ici)
        goal_msg.goal_pose.pose.orientation = orientation #Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)

        # Attendre que le serveur d'action soit prêt
        self._action_client.wait_for_server()

        # Envoyer l'objectif de manière asynchrone et ajouter un callback pour la réponse
        future = self._action_client.send_goal_async(goal_msg)
        future.add_done_callback(lambda future: self._goal_response_callback(future, callback))

    def _goal_response_callback(self, future, callback):
        """
        Callback appelé une fois que l'action est terminée.
        :param future: Le résultat de l'action.
        :param callback: Fonction de callback passée pour indiquer la fin de l'action.
        """
        result = future.result()
        if result:
            self.node.get_logger().info(f"Navigation terminée avec succès. Status: {result.status}")
        else:
            self.node.get_logger().error("Échec de la navigation.")

        # Appeler le callback pour indiquer que l'action est terminée
        callback(result)


