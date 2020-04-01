class DataProcessing:
    def process(self, data):
        """
        Process all the data

        args:
            data: data to process

        return:
            Processed data
        """
        # shortcut in case that there is nothing to process
        if len(data["dates"]) <= 1:
            return dict(dates=[])

        # process the data secuencially in pairs
        for i in range(1, len(data["dates"])):
            self.process_interval(data["dates"][i-1],
                                  data["dates"][i],
                                  data["weights"])

        return data

    def process_interval(self, date_old, date_new, weights):
        """
        Process a pair of dates, calculate the security return, 
        date return and date price

        args:
            date_old: date of t-1
            date_new: date of t
            weights: weights of securities
        return:
            date of t update with securities and index updated
        """

        # variable to accumulate the date return value
        return_index = 0
        # calculate security return
        for security_old, security_new in zip(date_old["securities"], date_new["securities"]):
            # rti = (Pit/Pi(t-1)) - 1 
            security_new["security_return"] = (
                security_new["price"] / security_old["price"]) - 1
            # Rt = sum(wi * rit)
            return_index += weights[security_new["fk_weight"]
                                    ]["value"] * security_new["security_return"]

        date_new["date_return"] = return_index
        # Pt = Pt-1 * (1 + Rt)
        date_new["price"] = date_old["price"] * \
            (1 + date_new["date_return"])

        return date_new