import simpy
import random

# =====================================================
# Paint Shop Conveyor System Simulation
# =====================================================

# -------------------------
# Simulation Configuration
# -------------------------

SIMULATION_TIME = 480

ARRIVAL_MIN = 8
ARRIVAL_MAX = 12

CLEAN_MIN = 15
CLEAN_MAX = 20

PRIMER_MIN = 25
PRIMER_MAX = 35

PAINT_MIN = 30
PAINT_MAX = 40

random.seed(42)

# -------------------------
# Metrics
# -------------------------

cars_completed = 0
alerts = 0

system_times = []

queue_wait = {
    "Cleaning": [],
    "Primer": [],
    "Painting": []
}

max_queue = {
    "Cleaning": 0,
    "Primer": 0,
    "Painting": 0
}

busy_time = {
    "Cleaning": 0,
    "Primer": 0,
    "Painting": 0
}

# =====================================================
# Paint Shop Class
# =====================================================

class PaintShop:

    def __init__(self, env):

        self.env = env

        self.cleaning_station = simpy.Resource(env, capacity=1)

        self.primer_station = simpy.Resource(env, capacity=2)

        self.paint_station = simpy.Resource(env, capacity=1)
            # -------------------------
    # Cleaning Process
    # -------------------------
    def cleaning_process(self, car_id):

        global alerts

        arrival_time = self.env.now

        if len(self.cleaning_station.queue) > max_queue["Cleaning"]:
            max_queue["Cleaning"] = len(self.cleaning_station.queue)

        if len(self.cleaning_station.queue) > 3:
            alerts += 1
            print(f"ALERT: Queue at Cleaning has {len(self.cleaning_station.queue)} cars waiting at time {self.env.now:.2f}")

        with self.cleaning_station.request() as request:

            yield request

            wait = self.env.now - arrival_time
            queue_wait["Cleaning"].append(wait)

            print(f"{self.env.now:.2f} --> Car {car_id} START Cleaning")

            process_time = random.uniform(CLEAN_MIN, CLEAN_MAX)

            busy_time["Cleaning"] += process_time

            yield self.env.timeout(process_time)

            print(f"{self.env.now:.2f} --> Car {car_id} FINISH Cleaning")

    # -------------------------
    # Primer Process
    # -------------------------
    def primer_process(self, car_id):

        global alerts

        arrival_time = self.env.now

        if len(self.primer_station.queue) > max_queue["Primer"]:
            max_queue["Primer"] = len(self.primer_station.queue)

        if len(self.primer_station.queue) > 3:
            alerts += 1
            print(f"ALERT: Queue at Primer has {len(self.primer_station.queue)} cars waiting at time {self.env.now:.2f}")

        with self.primer_station.request() as request:

            yield request

            wait = self.env.now - arrival_time
            queue_wait["Primer"].append(wait)

            print(f"{self.env.now:.2f} --> Car {car_id} START Primer")

            process_time = random.uniform(PRIMER_MIN, PRIMER_MAX)

            busy_time["Primer"] += process_time

            yield self.env.timeout(process_time)

            print(f"{self.env.now:.2f} --> Car {car_id} FINISH Primer")

    # -------------------------
    # Painting Process
    # -------------------------
    def painting_process(self, car_id):

        global alerts

        arrival_time = self.env.now

        if len(self.paint_station.queue) > max_queue["Painting"]:
            max_queue["Painting"] = len(self.paint_station.queue)

        if len(self.paint_station.queue) > 3:
            alerts += 1
            print(f"ALERT: Queue at Painting has {len(self.paint_station.queue)} cars waiting at time {self.env.now:.2f}")

        with self.paint_station.request() as request:

            yield request

            wait = self.env.now - arrival_time
            queue_wait["Painting"].append(wait)

            print(f"{self.env.now:.2f} --> Car {car_id} START Painting")

            process_time = random.uniform(PAINT_MIN, PAINT_MAX)

            busy_time["Painting"] += process_time

            yield self.env.timeout(process_time)

            print(f"{self.env.now:.2f} --> Car {car_id} FINISH Painting")
            # =====================================================
# Car Process
# =====================================================

def car(env, car_id, shop):

    global cars_completed

    print(f"{env.now:.2f} --> Car {car_id} ARRIVED")

    start_time = env.now

    # Cleaning
    yield env.process(shop.cleaning_process(car_id))

    # Primer
    yield env.process(shop.primer_process(car_id))

    # Painting
    yield env.process(shop.painting_process(car_id))

    finish_time = env.now

    cars_completed += 1

    system_times.append(finish_time - start_time)

    print(f"{finish_time:.2f} --> Car {car_id} EXITED SYSTEM")


# =====================================================
# Car Generator
# =====================================================

def car_generator(env, shop):

    car_id = 1

    while True:

        # Stop generating new cars after 480 minutes
        if env.now >= SIMULATION_TIME:
            break

        env.process(car(env, car_id, shop))

        inter_arrival = random.uniform(ARRIVAL_MIN, ARRIVAL_MAX)

        yield env.timeout(inter_arrival)

        car_id += 1


# =====================================================
# Simulation Runner
# =====================================================

env = simpy.Environment()

paint_shop = PaintShop(env)

env.process(car_generator(env, paint_shop))

env.run()
# =====================================================
# Final Report
# =====================================================

print("\n")
print("=" * 50)
print("=== Paint Shop Simulation Results (480 Minutes) ===")
print("=" * 50)

print(f"\nTotal Cars Completed : {cars_completed}")

if len(system_times) > 0:
    avg_system_time = sum(system_times) / len(system_times)
else:
    avg_system_time = 0

print(f"Average Time in System : {avg_system_time:.2f} minutes")


for station in ["Cleaning", "Primer", "Painting"]:

    if len(queue_wait[station]) > 0:
        avg_wait = sum(queue_wait[station]) / len(queue_wait[station])
    else:
        avg_wait = 0

        if station == "Primer":
         utilization = (busy_time[station] / (SIMULATION_TIME * 2)) * 100
else:
    utilization = (busy_time[station] / SIMULATION_TIME) * 100

    print("\n--------------------------------")

    print(f"Station : {station}")

    print(f"Utilization : {utilization:.2f}%")

    print(f"Maximum Queue Length : {max_queue[station]}")

    print(f"Average Waiting Time : {avg_wait:.2f} minutes")

print("\n--------------------------------")

print(f"Alerts Triggered : {alerts}")

print("=" * 50)