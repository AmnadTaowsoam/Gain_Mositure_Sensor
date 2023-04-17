from pyModbusTCP.client import ModbusClient
import time
import statistics
import plotly.express as px
import plotly.io as pio

class MoistureSensor:
    def __init__(self, host='192.168.200.100', port=502, address=400, num_registers=10):
        self.host = host
        self.port = port
        self.address = address
        self.num_registers = num_registers
        self.client = ModbusClient(host=self.host, port=self.port, auto_open=True)

    def read_data(self):
        return self.client.read_holding_registers(self.address, self.num_registers)
    
    def close_connection(self):
        self.client.close()
    
    def calculate_moisture_percentage(self,filtered_data):
        moisture_percentage = []
        for value in filtered_data:
            if value <= 800:
                k = 0.01
            elif 800 < value <= 1200:
                k = 0.02
            elif 1201 < value <= 1300:
                k = 0.03
            elif 1301 < value <= 1400:
                k = 0.03
            elif 1401 < value <= 1600:
                k = 0.04
            else:
                k = 0.05
            moisture_percentage.append(value * k)
        return moisture_percentage
    
    def calculate_stats(self):
        data = self.calculate_moisture_percentage()
        count = len(data)
        min_value = min(data)
        max_value = max(data)
        mean_value = statistics.mean(data)
        stddev_value = statistics.stdev(data)
        return count, min_value, max_value, mean_value, stddev_value
        
    def plot_moisture_percentage(self, moisture_percentages):
        fig = px.line(x=list(range(len(moisture_percentages))), y=moisture_percentages, title="Moisture Percentage", markers=True)
        return fig
          

# if __name__ == "__main__":
#     sensor = MoistureSensor()
#     moisture_percentages = []

#     try:
#         for i in range(10):  # Change this value to read data for a different number of iterations
#             data = sensor.read_data()
#             if data:
#                 print("Raw moisture sensor data:", data)
#                 filtered_data = [value for value in data if value > 800]
#                 print("Filtered moisture sensor data:", filtered_data)
#                 moisture_percentage = sensor.calculate_moisture_percentage(filtered_data)
#                 print("Moisture percentage:", moisture_percentage)
#                 moisture_percentages.extend(moisture_percentage)
#             else:
#                 print("Failed to read data from the moisture sensor")
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Stopped reading data from the moisture sensor")
#     finally:
#         sensor.close_connection()

#     fig = sensor.plot_moisture_percentage(moisture_percentages)
#     pio.write_html(fig, file='moisture_percentage_plot.html', auto_open=True)



