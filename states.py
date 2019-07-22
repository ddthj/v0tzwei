from objects import Vector3
from util import *

def kickoff(agent):
    if len(agent.friends) > 0:
        position = 0
        my_dist = (agent.ball.location - agent.me.location).magnitude()
        for friend in agent.friends:
            dist = (agent.ball.location - friend.location).magnitude()
            if dist < my_dist-20:
                position -= 1
        if position == -1:
            agent.c.__init__()
        elif position == -2:
            agent.defend.execute(agent)
        else:
            vector = (agent.ball.location - agent.me.location)
            target = agent.ball.location + (vector*10)
            targetShot(agent,target)
            local = agent.me.matrix.dot(vector)
            if vector.magnitude() < 700:
                flip(agent,local)
    else:
        vector = (agent.ball.location - agent.me.location)
        target = agent.ball.location + (vector*10)
        targetShot(agent,target)
        local = agent.me.matrix.dot(vector)
        if vector.magnitude() < 700:
            flip(agent,local)

class defend:
    def __init__(self):
        self.step = 0

    def panic(self,agent):
        goal_to_ball = (agent.ball.location-agent.my_goal).normalize()
        distance = (agent.ball.location-agent.my_goal).magnitude()
        time_estimate = distance / cap(-goal_to_ball.dot(agent.ball.velocity),0.001,4000)
        if time_estimate < 4.5 or distance < 2000:
            return True
        return False
    
    def execute(self,agent):
        if self.step == 0:
            goal_to_ball = (agent.ball.location-agent.my_goal).normalize()
            distance = (agent.ball.location-agent.my_goal).magnitude()
            vectorAlign(agent, agent.my_goal, goal_to_ball)
            if self.panic(agent) == True:
                self.step = 1
        elif self.step == 1:
            if self.panic(agent) == False:
                self.step = 0
            left =  agent.ball.location - Vector3(-1050*side(agent.team), side(agent.team)*5150, 0)
            right = agent.ball.location - Vector3(1050*side(agent.team), side(agent.team)*5150, 0)
            
            vector = (agent.ball.location - agent.me.location).normalize().clamp(right,left)
            target = agent.ball.location + (vector*1000)
            targetShot(agent,target)
                  
def targetShot(agent,target):
    temp = target - agent.ball.location
    vector = temp.normalize()
    cross = vector.cross(Vector3(0,0,1))

    distance=(agent.me.location - agent.ball.location).magnitude()
    drive_target = agent.ball.location + (cross * cap(cross.dot(agent.ball.velocity),-distance/6,distance/6)) + (vector*(-distance/2))

    control(agent,drive_target,2300)
    
    agent.renderer.begin_rendering("targetshot")
    agent.renderer.draw_line_3d(agent.ball.location,target, agent.renderer.create_color(255,255,0,255))
    agent.renderer.draw_rect_3d(drive_target, 10,10, True, agent.renderer.create_color(255,0,255,0))
    agent.renderer.end_rendering()
    

def vectorAlign(agent,target,vector):
    projection_distance = vector.dot(agent.me.location-target)
    projection_point = target +(vector*projection_distance)
    local_v = agent.me.matrix.dot(agent.me.velocity)[0]
    dist_to_projection = (agent.me.location-projection_point).magnitude()

    forward_target = (target + (vector*(projection_distance+500)))
    reverse_target = (target + (vector*(projection_distance-500)))

    local_align = agent.me.matrix.dot(forward_target-agent.me.location)
    aligned = True if abs(math.atan2(local_align[1],local_align[0])) < 1.0 and dist_to_projection < 150 else False

    if dist_to_projection >=300:
        speed = cap((dist_to_projection-500)*2,300,2300)
        control(agent,target,speed)
        final_target = target
    else:
        if not aligned:
            control(agent,forward_target,300)
            final_target = forward_target
        else:
            if projection_distance > 0:
                speed = cap((projection_distance-500)*2,300,2300)
                control(agent,reverse_target,speed,-1)
                final_target = reverse_target
            else:
                speed = cap((projection_distance-500)*2,300,2300)
                control(agent,forward_target,speed)
                final_target = forward_target
                
    agent.renderer.begin_rendering("vecalign")
    agent.renderer.draw_rect_3d(target, 10,10, True, agent.renderer.create_color(255,255,0,0))
    agent.renderer.draw_line_3d(target, target+(vector*1000), agent.renderer.white())
    agent.renderer.draw_rect_3d(final_target, 10,10, True, agent.renderer.create_color(255,0,0,255))
    agent.renderer.end_rendering()

def control(agent,target,speed,direction = 1):
    local_t = agent.me.matrix.dot(target-agent.me.location)
    local_v = agent.me.matrix.dot(agent.me.velocity)[0]

    angles = defaultPD(agent,local_t)
    
    if abs(angles[2]) > 1.57 and direction == 1:
        agent.c.handbrake = True
    else:
        agent.c.handbrake = False
    defaultThrottle(agent,speed,local_v,direction)
