import shelve

if __name__ == "__main__":
    db = shelve.open("lampi_state", writeback=True)

    # db["bpm"] = 100
    # db.sync()

    # print(db["bpm"])