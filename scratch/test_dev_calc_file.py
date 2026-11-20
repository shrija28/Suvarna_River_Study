import sys, os, traceback
log_file = r"d:\Suvarna_River_Study\scratch\test_output.txt"
with open(log_file, "w") as f:
    f.write("Starting...\n")
    try:
        sys.path.insert(0, r"d:\Suvarna_River_Study\qt_version")
        sys.path.insert(0, r"d:\Suvarna_River_Study")
        f.write("Importing deviation_service...\n")
        from backend.deviation_service import deviation_service
        f.write("Imported deviation_service!\n")
        years = deviation_service.get_available_years()
        f.write(f"Years: {years}\n")
        res = deviation_service.calculate_deviation(1989, 2000)
        f.write(f"Result 1989-2000: {res is not None}\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
        traceback.print_exc(file=f)
