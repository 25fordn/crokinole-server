# from CrokinoleGUI import UIPost, UIItem
from math import pi, sin, cos, sqrt, atan, asin, acos

from settings import Settings

class Item():
    def __init__(self, pos, radius, color, mass, velocity, is_puck):
        self.pos_chain = [pos]
        self.is_in_event = [True]
        self.radius = radius
        self.color = color
        self.mass = mass
        self.velocity_chain = [velocity]
        self.in_event = [False]
        self.is_puck = is_puck

        
class Board():
    
    def __init__(self, settings):
        self.settings = settings
        
        r_posts = self.settings.r_posts
        self.items = []
        # self.collission_chain = []
        for i in range(8):
            angle = 2*pi * (i/8 + 1/16)
            pos = (r_posts *sin(angle), r_posts * cos(angle))
            color = "gray"
            mass = 1
            velocity = (0, 0)
            is_puck = False
            radius = self.settings.r_post
            self.items.append(Item(pos, radius, color, mass, velocity, False))
            
        pos = (-304.8, 0)
        radius = 15
        color = "green"
        mass = 0.3
        velocity = (1000, 0)
        is_puck = True
        self.items.append(Item(pos, radius, color, mass, velocity, is_puck))
        
        pos = (-200, 10)
        radius = 15
        color = "blue"
        mass = 0.3
        velocity = (0, 0)
        is_puck = True
        self.items.append(Item(pos, radius, color, mass, velocity, is_puck))
        
        self.last_collission_items = set()    
    
    def calc_item_collission(self, collission):
        t, v_Axi, alpha, D, D_collission, item_A, item_B = collission
        r_A, r_B = item_A.radius, item_B.radius
        m_A, m_B = item_A.mass, item_B.mass
        sin_alpha = sin(alpha)
        
        vvx, vvy = (item_A.velocity_chain[-1][0]/v_Axi, 
                    item_A.velocity_chain[-1][1]/v_Axi)
        if item_B.is_puck:
            C_R = self.settings.C_R 
            v_Axf = v_Axi*(C_R*D**2*m_B*sin_alpha**2 - C_R*m_B*r_A**2 - 2*C_R*m_B*r_A*r_B - C_R*m_B*r_B**2 + D**2*m_B*sin_alpha**2 + m_A*r_A**2 + 2*m_A*r_A*r_B + m_A*r_B**2)/(m_A*r_A**2 + 2*m_A*r_A*r_B + m_A*r_B**2 + m_B*r_A**2 + 2*m_B*r_A*r_B + m_B*r_B**2)
            v_Ayf = D*m_B*v_Axi*(C_R*D**2*sin_alpha**2 - C_R*r_A**2 - 2*C_R*r_A*r_B - C_R*r_B**2 + D**2*sin_alpha**2 - r_A**2 - 2*r_A*r_B - r_B**2)*sin_alpha/(sqrt((-D**2*sin_alpha**2 + r_A**2 + 2*r_A*r_B + r_B**2)/(r_A**2 + 2*r_A*r_B + r_B**2))*(m_A*r_A**3 + 3*m_A*r_A**2*r_B + 3*m_A*r_A*r_B**2 + m_A*r_B**3 + m_B*r_A**3 + 3*m_B*r_A**2*r_B + 3*m_B*r_A*r_B**2 + m_B*r_B**3))
            v_Bxf = m_A*v_Axi*(-C_R*D**2*sin_alpha**2 + C_R*r_A**2 + 2*C_R*r_A*r_B + C_R*r_B**2 - D**2*sin_alpha**2 + r_A**2 + 2*r_A*r_B + r_B**2)/(m_A*r_A**2 + 2*m_A*r_A*r_B + m_A*r_B**2 + m_B*r_A**2 + 2*m_B*r_A*r_B + m_B*r_B**2)
            v_Byf = D*m_A*v_Axi*(-C_R*D**2*sin_alpha**2 + C_R*r_A**2 + 2*C_R*r_A*r_B + C_R*r_B**2 - D**2*sin_alpha**2 + r_A**2 + 2*r_A*r_B + r_B**2)*sin_alpha/(sqrt((-D**2*sin_alpha**2 + r_A**2 + 2*r_A*r_B + r_B**2)/(r_A**2 + 2*r_A*r_B + r_B**2))*(m_A*r_A**3 + 3*m_A*r_A**2*r_B + 3*m_A*r_A*r_B**2 + m_A*r_B**3 + m_B*r_A**3 + 3*m_B*r_A**2*r_B + 3*m_B*r_A*r_B**2 + m_B*r_B**3))
            v_Axf_rot, v_Ayf_rot = (v_Axf*vvx - v_Ayf*vvy, v_Axf*vvy + v_Ayf*vvx)
            v_Bxf_rot, v_Byf_rot = (v_Bxf*vvx - v_Byf*vvy, v_Bxf*vvy + v_Byf*vvx)
            item_A.velocity_chain[-1] = (v_Axf_rot, v_Ayf_rot)
            item_B.velocity_chain[-1] = (v_Bxf_rot, v_Byf_rot)
        else:
            C_R = self.settings.C_R_post
            v_Axf = v_Axi*(C_R*D**2*sin_alpha**2 - C_R*r_A**2 - 2*C_R*r_A*r_B - C_R*r_B**2 + D**2*sin_alpha**2)/(r_A**2 + 2*r_A*r_B + r_B**2)
            v_Ayf = -D*v_Axi*sqrt((-D**2*sin_alpha**2 + r_A**2 + 2*r_A*r_B + r_B**2)/(r_A**2 + 2*r_A*r_B + r_B**2))*(C_R + 1)*sin_alpha/(r_A + r_B)                   
            v_Axf_rot, v_Ayf_rot = (v_Axf*vvx - v_Ayf*vvy, v_Axf*vvy + v_Ayf*vvx)
            item_A.velocity_chain[-1] = (v_Axf_rot, v_Ayf_rot)
        
    
    def collission_state(self, item_A, item_B):
        x_B, y_B = item_B.pos_chain[-1]
        v_Ax, v_Ay = item_A.velocity_chain[-1]
        x_A, y_A = item_A.pos_chain[-1]
        r_A, r_B = item_A.radius, item_B.radius
        
        mu = self.settings.mu
        g = self.settings.grav
        
        delta_x, delta_y = x_B - x_A, y_B - y_A
        D = sqrt(delta_x**2 + delta_y**2)
        v_A = sqrt(v_Ax**2 + v_Ay**2)
        if (r_A + r_B) < D:
            angle_range = asin((r_A + r_B) / D)
        else:
            angle_range = pi/2
        alpha = acos((delta_x * v_Ax + delta_y * v_Ay) / (D * v_A))
        if alpha < angle_range:
            if (delta_x * v_Ay - delta_y * v_Ax) > 0:
                alpha = -alpha
            theta = asin(D * sin(alpha) / (r_A + r_B))
            D_collission = sqrt(D**2 + (r_A+r_B)**2 - 2*(D*(r_A+r_B)*cos(theta-alpha)))
            D_max_slide = v_A**2 / (2*mu*g)
            if D_collission < D_max_slide:
                t = (v_A - sqrt(v_A**2 - 2*mu*g*D_collission))/(mu*g)
                v_Axi = v_A - mu*g*t
                if t < 0:
                    print(t, v_Axi, alpha, D, D_collission, item_A, item_B)
                    return None
                return t, v_Axi, alpha, D, D_collission, item_A, item_B
        return None
    
    def find_next_collission(self):
        items = self.items
        possible_collissions = []
        
        mu = self.settings.mu
        g = self.settings.grav
        
        for item_A in items:
            vAxi, vAyi = item_A.velocity_chain[-1]
            vAi = sqrt(vAxi**2 + vAyi**2)
            if vAi > 0.001:
                for item_B in items:
                    if item_B.is_puck:
                        if (item_A != item_B) and (self.last_collission_items != set([item_A, item_B])):
                            vBxi, vByi = item_B.velocity_chain[-1]
                            if abs(vBxi) < 0.001 and abs(vByi) < 0.001:
                                cs = self.collission_state(item_A, item_B)
                                if cs:
                                    possible_collissions.append(cs)
                            else:
                                print("Both moving - possible wrong result")
                        else:
                            t_stop = vAi / (mu*g)
                            D_stop = vAi*vAi / (2*mu*g)
                            possible_collissions.append([t_stop, 0, 0, 0, D_stop, item_A, None])
                    else:
                        cs = self.collission_state(item_A, item_B)
                        if cs:
                            possible_collissions.append(cs)               
        if possible_collissions:
            next_collission = min(possible_collissions, key=lambda x: x[0])
            t, v_Axi, alpha, D, D_collission, item_A, item_B = next_collission
            # for val in next_collission:
            #     if type(val) == float:
            #         out = f'{val:.5f}'
            #     elif val == None:
            #         out = 'None'
            #     else:
            #         out = str(val)
            #     print(f'{out:>8}', end=' ')
            # print()
            self.last_collission_items = set([item_A, item_B])
            return next_collission
        else:
            return None

        
    def move_items(self, t, item_A, item_B):
        items = self.items
        mu = self.settings.mu
        g = self.settings.grav
        
        for item in items:
            if item.is_puck:
                xi, yi = item.pos_chain[-1] 
                vxi, vyi = item.velocity_chain[-1]
                vi = sqrt(vxi**2 + vyi**2)
                if vi > 0.0001:
                    vvx, vvy = vxi/vi, vyi/vi
                    D = -mu*g*t*t/2 + vi*t
                    vf = -mu*g*t + vi
                    new_velocity = (vf*vvx, vf*vvy)
                    new_position = (xi + D*vvx, yi + D*vvy)
                # else:
                #     new_velocity = (0, 0)
                #     new_position = (xi, yi)
                    item.pos_chain.append(new_position)
                    item.is_in_event.append((item == item_A) or (item == item_B))
                    item.velocity_chain.append(new_velocity)
    
                
    def find_collission_chain(self):     
        self.last_collission_items = set()
        next_collission = self.find_next_collission()
        while next_collission: # and (len(item_states) < 100):
            t, v_Axi, alpha, D, D_collission, item_A, item_B =  next_collission
            self.move_items(t, item_A, item_B)
            if item_B:
                self.calc_item_collission(next_collission)
            next_collission = self.find_next_collission()
        

if __name__ == '__main__':
    settings = Settings()
    board = Board(settings)
    board.find_collission_chain()
    print()
    print('board.items[8].pos_chain:', board.items[8].pos_chain)
    print('board.items[8].velocity_chain:', board.items[8].velocity_chain)
    print('board.items[9].pos_chain:', board.items[9].pos_chain)
    print('board.items[9].velocity_chain:', board.items[9].velocity_chain)

