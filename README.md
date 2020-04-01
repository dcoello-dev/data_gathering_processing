
# Design of the architecture

In the description of the problem we can identify 3 types of applications as well as a set of requirements.

## Applications

- Data gathering applications
- Data processing applications
- Data visualization tools


## Requirements

- Data is going to be collected from different sources on real time
- Data have to be stored in a database
- Data processing can be done on the fly
- Complex data processing need to be calculated in advance and stored on the database
- Data might be of interest to several processed simultaneously




# POC implementation

Implementation have two main processes, one for data gathering simulation and other for data processing, for the persistence I used mysql-server due was already installed in my dev environment, any other SQL database should work.

It is also provided the create.sql script, to insert the initial Data its enough to run the data gathering process

For convenience for this POC both implementations are in the same directory, specific classes are implemented under app directory and configuration file under conf directory

## Data gathering process

It simulates data gathering generating random prices for random dates, the timestamps are simulated with integers in between 0 and 10.
It simulates also the subscription of the data processing process sending an empty message through sockets every tame that inserts or updates a Date.

to start this process:

```bash
python3 data_gathering.py
```

If you start it in foreground logging system will inform you about the updates

## Data processing process

When receives a message through socket it starts the processing

Processing starts discovering wich date had been updated, then it takes all the dates from the previous date of the update to the last one then, it process the new values and finally stores the new values updating the database

Price series can be accesed through http on the port 5000 in json format

To start this process

```bash
python3 data_processing.py
```

In order to trigger the data processing remember to launch the data gathering process at the same time, you can also trigger the process sending a notification with netcat

```bash
nc localhost 25000
```

To check results query the database or check the json output on http://localhost:5000

## Possible improvements

- Solve all TODOS
- Better format to the price series json output
- Improve SQL queries for better performance
- Implement a better system for notification instead of simulation with sockets(mqtt?, GrapQL??)
- Define interfaces and factories for DataHandler, DataProcesing, DatabaseConnection, HttpInterface and notification_service in order to be able to easily modify and extend the specific implementations
- The actual approach of the data processing process should be implemented with a Singleton pattern ensuring that only one instance of the process can run at the same time, if horizontal scalability is required here should be followed a different solution design
- Unitary test and system test
- Benchmarking