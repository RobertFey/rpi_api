from flask import Flask, jsonify
import subprocess


app = Flask(__name__)

info_items = [
    {"name": "cpu_temperature", "attributes": {}},
    {"name": "free_storage", "attributes": {}},
    {"name": "free_memory", "attributes": {}},
    {"name": "sensors", "attributes": {}},
    {"name": "test", "attributes": {}},
    ]

def get_cpu_temp():
    # temp=55.8'C
    try:
        out = subprocess.Popen(['cat', '/sys/class/thermal/thermal_zone0/temp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # out = subprocess.Popen(['/opt/vc/bin/vcgencmd', 'measure_temp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = out.stdout.readline()
        out = out.decode().strip()
        out = float(out) / 1000
        #out = out.decode().strip().split('=')[-1].split("'")[0].strip()
        return out
    except Exception as inst:
        print(inst)
        return None
    
def get_hostname():
    # hassbian
    try:
        out = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = out.stdout.readline().strip().decode().strip()
        return str(out)
    except:
        return None

def get_free_storage():
    # df / -h -B M
    # Filesystem     1M-blocks   Used Available Use% Mounted on
    # /dev/root         30074M 12495M    16325M  44% /
    try:
        out = subprocess.Popen(['df', '/', '-h', '-B', 'M'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = out.stdout.readlines()
        out = out[-1].decode().split()
        size_used = out[2][:-1].strip()
        size_free = out[3][:-1].strip()
        perc_used = out[4][:-1].strip()
        return float(size_free)
    except Exception as inst:
        print(inst)
        return None

def get_test():
    try:
        out = subprocess.Popen(['pwd'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = out.stdout.readline()
        out = out.decode()
        return out
    except Exception as inst:
        print(inst)
        return None

def get_uptime():
    #  17:43:01 up 35 days, 20:59,  2 users,  load average: 0.18, 0.26, 0.20
    try:
        out = subprocess.Popen(['uptime'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = out.stdout.readline()
        out = out.decode().strip()
        if "load average:" in out:
            cpu_avg_1_min = float(out.split(',')[-3].split(' ')[-1].strip()) # 0.18
            cpu_avg_5_min = float(out.split(',')[-2].strip()) # 0.26
            cpu_avg_15_min = float(out.split(',')[-1].strip()) # 0.20
        else:
            cpu_avg_1_min = None
            cpu_avg_5_min = None
            cpu_avg_15_min = None
        return (out, cpu_avg_1_min, cpu_avg_5_min, cpu_avg_15_min)
    except Exception as inst:
        print(inst)
        return None, None, None, None

def get_free_memory():
    # free -m -w -t
    #               total        used        free      shared     buffers       cache   available
    # Mem:            926         417          68          55          62         377         402
    # Swap:            99          99           0
    # Total:         1026         517          68
    try:
        out = subprocess.Popen(['free', '-m', '-w', '-t'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = out.stdout.readlines()
        out = out[1].decode().split()
        size_used = out[2].strip()
        size_free = out[3].strip()
        # size_available = out[7].strip()
        return float(size_free)
    except Exception as inst:
        print(inst)
        return None

@app.route('/system/<string:name>')
def System_info(name):
    for item in info_items:
        if item['name'] == name:
            if name == "cpu_temperature":
                return jsonify({"name": name, "id": get_hostname(), "unit_of_measurement": "Celcius", "value": get_cpu_temp()}), 200
            elif name == "free_storage":
                return jsonify({"name": name, "id": get_hostname(), "unit_of_measurement": "GB", "value": get_free_storage()}), 200
            elif name == "free_memory":
                return jsonify({"name": name, "id": get_hostname(), "unit_of_measurement": "MB", "value": get_free_memory()}), 200                    
            elif name == "sensors":
                return jsonify({
                    "attributes": {
                        "cpu_temperature": {
                            "name": "CPU Temperature",
                            "value": get_cpu_temp(), 
                            "unit_of_measurement": "Celcius",
                            }, 
                        "free_storage": {
                            "name": "Free Storage",
                            "value": get_free_storage(), 
                            "unit_of_measurement": "GB",
                            }, 
                        "free_memory": {
                            "name": "Free Memory",
                            "value": get_free_memory(), 
                            "unit_of_measurement": "MB",
                            },
                        "avg_cpu_load_1_min": {
                            "name": "AVG CPU load 1 min",
                            "value": get_uptime()[1], 
                            "unit_of_measurement": "load",
                            },
                        "avg_cpu_load_5_min": {
                            "name": "AVG CPU load 5 min",
                            "value": get_uptime()[2], 
                            "unit_of_measurement": "load",
                            },
                        "avg_cpu_load_15_min": {
                            "name": "AVG CPU load 15 min",
                            "value": get_uptime()[3], 
                            "unit_of_measurement": "load",
                            },
                        "id": get_hostname(),
                        "name": name,
                        "uptime": get_uptime()[0],
                        },
                    }), 200                    
            elif name == "test":
                return jsonify({"name": name, "id": get_hostname(), "unit_of_measurement": "", "value": get_test()}), 200                    
    return jsonify({"name": name, "id": get_hostname(), "unit_of_measurement": None, "value": None}), 404


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=False, port=80)
