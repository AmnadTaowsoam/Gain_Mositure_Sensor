from pyModbusTCP.client import ModbusClient
import time
import statistics
import plotly.express as px
import plotly.io as pio
import numpy as np

class MoistureSensor:
    def __init__(self, host='192.168.200.100', port=502, address=403, num_registers=10):
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
                k = 100
            elif 800 < value <= 1492:
                k = 1.16
            elif 1493 < value <= 1610:
                k = 1.106
            elif 1611 < value <= 1693:
                k = 1.152
            elif 1694 < value <= 1777:
                k = 1.05
            else:
                k = 1.05
            moisture_percentage.append((value / k)/100)
        return moisture_percentage
    
    def find_best_threshold(self,moisture_percentage):
        # Compute the histogram of the data
        hist, bins = np.histogram(moisture_percentage, bins=50)
        
        # Compute the cumulative sum of the histogram
        cumsum = np.cumsum(hist)
        
        # Compute the ratios of the cumulative sum to the total number of data points
        ratios = cumsum / len(moisture_percentage)
        
        # Find the index of the first ratio greater than or equal to 0.1 and the last ratio less than or equal to 0.9
        start_index = np.argmax(ratios >= 0.1)
        end_index = len(ratios) - 1 - np.argmax(np.flip(ratios) <= 0.9)
        
        # Compute the mean of the data points in the range [bins[start_index], bins[end_index]]
        mean = np.mean([value for value in moisture_percentage if bins[start_index] <= value <= bins[end_index]])
        
        # Compute the threshold as the mean of the data points in the range [bins[start_index], bins[end_index]]
        threshold = mean
        
        return threshold
    
    def select_similar_range(self,moisture_percentage, threshold):
        # Compute the difference between adjacent elements in the array
        diff = np.diff(moisture_percentage)
        
        # Find the indices where the difference is less than or equal to the threshold
        indices = np.where(diff <= threshold)[0]
        
        # Check if the first and last indices are adjacent
        if len(indices) > 0 and indices[0] == 0:
            indices = indices[1:]
        if len(indices) > 0 and indices[-1] == len(moisture_percentage) - 2:
            indices = indices[:-1]
        
        # Select the ranges of indices where the difference is less than or equal to the threshold
        ranges = []
        for i in range(len(indices)):
            if i == 0:
                ranges.append((0, indices[i] + 1))
            elif i == len(indices) - 1:
                ranges.append((indices[i], len(moisture_percentage)))
            else:
                ranges.append((indices[i], indices[i+1] + 1))
        
        # Select the subarrays corresponding to the ranges of indices
        result = [moisture_percentage[start:end] for start, end in ranges]
        
        return result
    
    def calculate_stats(self,moisture_range_homo):
        data = moisture_range_homo.copy()
        count = len(data)
        if len(data) > 0:
            min_value = round(min(data),2)
            max_value = round(max(data),2)
            mean_value = round(statistics.mean(data),2)
            stddev_value = round(statistics.stdev(data),2)
        else:
            min_value = None
            max_value = None
            mean_value = None
            stddev_value = None
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



