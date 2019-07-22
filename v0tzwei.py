import math

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from objects import *
from util import *
from states import *


class PythonExample(BaseAgent):

    def initialize_agent(agent):
        agent.c = SimpleControllerState()
        agent.sinceJump = 5.0
        agent.time = 0.0
        agent.me = carObject(agent.index)
        agent.ball = ballObject()
        agent.friends = []
        agent.foes = []
        agent.my_goal = Vector3(0,5200*side(agent.team),10)
        agent.foe_goal = Vector3(0,5200*-side(agent.team),10)

        agent.defend = defend()
        agent.kickoff = False
        

    def get_output(agent, packet: GameTickPacket) -> SimpleControllerState:
        agent.preprocess(packet)
        if agent.kickoff == True:
            kickoff(agent)
        else:
            if len(agent.friends) > 0:
                position = 0
                my_dist = (agent.ball.location - agent.me.location).magnitude()
                for friend in agent.friends:
                    dist = (agent.ball.location - friend.location).magnitude()
                    if dist < my_dist-20:
                        position -= 1
                if position == -2 or agent.defend.step == 1:
                    agent.defend.execute(agent)
                elif position == -1:
                    target = (agent.my_goal + agent.ball.location) * 0.5
                    vectorAlign(agent,target,(agent.ball.location-agent.me.location).normalize())
                else:
                    targetShot(agent,agent.foe_goal)
            else:
                targetShot(agent,agent.foe_goal)

        return agent.c
    
    def preprocess(agent,packet):
        elapsed = packet.game_info.seconds_elapsed - agent.time
        agent.sinceJump += elapsed
        agent.time = packet.game_info.seconds_elapsed

        agent.kickoff = packet.game_info.is_round_active and packet.game_info.is_kickoff_pause

        agent.ball.update(packet.game_ball)
        for i in range(packet.num_cars):
            car = packet.game_cars[i]
            if i == agent.index:
                agent.me.update(car)
            elif car.team == agent.team:
                flag = True
                for friend in agent.friends:
                    if friend.index == i:
                        friend.update(car)
                        flag = False
                if flag == True:
                    agent.friends.append(carObject(i,car))

def draw_debug(renderer, car, ball, action_display):
    renderer.begin_rendering()
    # draw a line from the car to the ball
    renderer.draw_line_3d(car.physics.location, ball.physics.location, renderer.white())
    # print the action that the bot is taking
    renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()
