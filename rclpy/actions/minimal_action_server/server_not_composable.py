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


async def execute_callback(goal):
    """Executes the goal."""
    feedback_msg = Fibonacci.Feedback()

    # append the seeds for the fibonacci sequence
    feedback_msg.sequence = [0, 1]

    # start executing the action
    for i in range(1, goal.request.order):
        if goal.is_cancel_requested():
            result = Fibonacci.Result()
            result.response = GoalResponse.CANCELLED
            return result
        feedback_msg.sequence.append(feedback_msg.sequence[i] + feedback_msg.sequence([i-1]))
        # publish the feedback
        goal.publish_feedback(feedback_msg)

        # Sleep for demonstration purposes
        asyncio.sleep(1)

    with g_lock:
        g_goal = None
    result = Fibonacci.Result()
    result.result.sequence = feedback_msg.sequence
    result.response = GoalResponse.SUCCEEDED
    return result


def main(args=None):
    rclpy.init(args=args)

    node = rclpy.create_node('minimal_action_server')

    action_server = ActionServer(
        node,
        Fibonacci,
        'fibonacci',
        goal_callback=lambda g: return GoalResponse.ACCEPT,
        cancel_callback=lambda g: return GoalResponse.ACCEPT,
        execute_callback=execute_callback)

    rclpy.spin(node)

    action_server.destroy()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()