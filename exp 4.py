import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May"]
sales = [12000, 18000, 15000, 22000, 20000]

# Bar Chart
plt.figure(figsize=(6,4))
plt.bar(months, sales)
plt.title("Monthly Sales - Bar Chart")
plt.xlabel("Months")
plt.ylabel("Sales")
plt.show()

# Line Graph
plt.figure(figsize=(6,4))
plt.plot(months, sales, marker='o')
plt.title("Monthly Sales - Line Graph")
plt.xlabel("Months")
plt.ylabel("Sales")
plt.grid(True)
plt.show()
