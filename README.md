# Green roof web server
## Creating the database
There is a sqlite database stored [here](./database/sql_app.sqlite)
### The steps required to make a new table for the database are as follows. Using water level sensors as an example.
1. Define the table layout in [this file](./SQL_app/models.py) e.g. 
```python
class WaterLevel(Base):
    __tablename__ = "water_levels"
    timestamp = Column(DateTime, primary_key=True, index=True)
    power = Column(Float)
    water_level1 = Column(Float)
    #...
    water_level10 = Column(Float)
```
2. Create a file e.g. data_parsers/water_level_parser.py.
This file should create a generator that returns the water level in chronological order. If no new data is available, it should yield `None`.
3. Update [this file](update_database.py) using your newly created generator add the new code to the file using `insert_temps` as a reference.
