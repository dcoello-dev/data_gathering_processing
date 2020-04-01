import json


class DataHandler:
    def __init__(self, conection):
        self.cnx = conection

    def get_price_series(self):
        """Return price series in json format"""
        series_query = "SELECT * from Date JOIN Security on " \
            "Date.timestamp = Security.fk_date " \
            "JOIN Weight on Security.fk_weight=Weight.id"
        self.cnx.connect()
        elems = self.cnx.execute_select(series_query)
        self.cnx.disconnect()
        return json.dumps(elems, indent=2)

    @staticmethod
    def assign_securities_to_dates(dates, securities, n_weights):
        """
        Given the dates and the securities append the securities of each date
        to the date dict for usability reasons

        args:
            dates: sorted array with the dates
            securities: sorted array with the securities
            n_weights: number of weights
        """
        # Assert that the data is correct
        assert len(securities) % n_weights == 0
        assert len(securities) / n_weights == len(dates)
        for i in range(0, len(securities), n_weights):
            dates[int(i/n_weights)]["securities"] = securities[i:i+n_weights]
        return dates

    def discovery(self):
        """Discover if from wich date it is necessary to 
        update the price series"""

        # Gather the timestamps from the dates that are updated
        discovery_query = "SELECT timestamp from Date " \
            "WHERE date_update=1 ORDER by timestamp"

        self.cnx.connect()
        elems = self.cnx.execute_select(discovery_query)

        # If there are no elements its not necessary to continue
        if len(elems) > 0:
            result = self.get_elems_to_update(elems[0]["timestamp"])
            self.cnx.disconnect()
            return result

        self.cnx.disconnect()

    def get_elems_to_update(self, index):
        """
        Given the index of the first date updated returns
        the weights and dates with securities that need to be updated

        args:
            index: integer with the index of the first updated date

        return:
            dictionary with weights and dates with its securities appended
        """
        # query to gather the dates with timestamp bigger than index - 1
        # sorted by timestamp
        # the query is from index-1 to simulate that is from the day before
        # of the update
        date_query = "SELECT timestamp, price, date_return "\
            "from Date WHERE timestamp>=" + \
            str(index - 1) + " ORDER by timestamp"

        # query to gather all the weights sorted by id
        weight_query = "SELECT * from Weight Order by id"

        dates = self.cnx.execute_select(date_query)
        weights = self.cnx.execute_select(weight_query)

        # Gather securities that its foreing key from date is index-1
        # due the same reasons that the date query, and sort the reslt by
        # the date key
        security_query = "SELECT * from Security WHERE fk_date>=" + \
            str(index - 1) + " ORDER by fk_date"
        securities = self.cnx.execute_select(security_query)

        # Format data for usability reasons
        dates = self.assign_securities_to_dates(
            dates, securities, len(weights))

        return dict(dates=dates,
                    weights=weights)

    def update_elements(self, data):
        """
        Update database with processed data

        args:
            data: processed data
        """

        def params_date(date):
            """function to generate date params for query"""
            return (date["price"],
                    date["date_return"],
                    date["timestamp"])

        def params_security(security):
            """function to generate security params for query"""
            return (security["security_return"],
                    security["fk_weight"],
                    security["fk_date"])

        update_date = "UPDATE Date set "\
            "price=%s, date_return=%s, date_update=0 "\
            "WHERE timestamp=%s"

        update_security = "UPDATE Security set security_return=%s "\
            "WHERE fk_weight=%s AND fk_date=%s"

        # build the querie tup with al the queries for the transaction
        queries_tup = []
        for date in data["dates"]:
            queries_tup.append((update_date, params_date(date)))
            for security in date["securities"]:
                queries_tup.append(
                    (update_security, params_security(security)))

        self.cnx.connect()
        self.cnx.execute_transaction(queries_tup)
        self.cnx.disconnect()
