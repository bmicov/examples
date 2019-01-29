# Copyright 2018 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from example_interfaces.action import Fibonacci

import rclpy
from rclpy.action import ActionServer
from rclpy.action import GoalResponse
from rclpy.node import Node
import threading


class MinimalActionServer(Node):
    """Minimal action server that processes one goal at a time."""

    def __init__(self):
        super().__init__('minimal_action_server')
        self._goal = None
        self._goal_lock = threading.Lock()
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            execute_callback=self.execute_callback)

    def destroy(self):
        self._action_server.destroy()
        super().destroy_node()

    def goal_callback(self, goal):
        """Accepts or rejects a client request to begin an action."""
        with self._goal_lock:
            # This server only allows one goal at a time
            if self._goal is not None:
                # Preempt existing goal
                self._goal.cancel()
            self._goal = goal
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal):
        """Accepts or rejects a client request to cancel an action."""
        return GoalResponse.ACCEPT

    async def execute_callback(self, goal):
        """Executes the goal."""
        feedback_msg = Fibonacci.Feedback()

        # Append the seeds for the Fibonacci sequence
        feedback_msg.sequence = [0, 1]

        # Start executing the action
        for i in range(1, goal.request.order):
            if goal.is_cancel_requested():
                result = Fibonacci.Result()
                result.response = GoalResponse.CANCELLED
                return result
            feedback_msg.sequence.append(feedback_msg.sequence[i] + feedback_msg.sequence([i-1]))
            # Publish the feedback
            goal.publish_feedback(feedback_msg)

            # Sleep for demonstration purposes
            asyncio.sleep(1)

        with self._goal_lock:
            self._goal = None
        result = Fibonacci.Result()
        result.result.sequence = feedback_msg.sequence
        result.response = GoalResponse.SUCCEEDED
        return result


def main(args=None):
    rclpy.init(args=args)

    action_server = MinimalActionServer()

    rclpy.spin(action_server)

    action_server.destroy()
    rclpy.shutdown()


if __name__ == '__main__':
    main()