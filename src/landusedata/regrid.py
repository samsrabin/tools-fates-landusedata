import xesmf as xe

def RegridConservative(ds_to_regrid, ds_regrid_target, regridder_weights, regrid_reuse):

    # define the regridder transformation
    regridder = GenerateRegridder(ds_to_regrid, ds_regrid_target, regridder_weights, regrid_reuse)

    # Loop through the variables to regrid
    ds_regrid = RegridLoop(ds_to_regrid, regridder)

    return (ds_regrid, regridder)

def GenerateRegridder(ds_to_regrid, ds_regrid_target, regridder_weights_file, regrid_reuse):

    regrid_method = "conservative"
    print("\nDefining regridder, method: ", regrid_method)

    if (regrid_reuse):
        regridder = xe.Regridder(ds_to_regrid, ds_regrid_target,
                                 regrid_method, weights=regridder_weights_file)
    else:
        regridder = xe.Regridder(ds_to_regrid, ds_regrid_target, regrid_method)

        # If we are not reusing the regridder weights file, then save the regridder
        filename = regridder.to_netcdf(regridder_weights_file)
        print("regridder saved to file: ", filename)

    return(regridder)

def RegridLoop(ds_to_regrid, regridder):

    # To Do: implement this with dask
    print("\nRegridding")

    # Loop through the variables one at a time to conserve memory
    ds_varnames = list(ds_to_regrid.variables.keys())
    varlen = len(ds_to_regrid.variables)
    first_var = False
    for i, var in enumerate(ds_to_regrid):

        # Skip time variable and only regrid variables that match the lat/lon shape.
        do_regrid = not "time" in var
        do_regrid = do_regrid and \
            ds_to_regrid[var][0].shape == (ds_to_regrid.lat.shape[0], ds_to_regrid.lon.shape[0])
        if not do_regrid :
            print("skipping variable {}/{}: {}".format(i+1, varlen, var))
            continue

        print("regridding variable {}/{}: {}".format(i+1, varlen, var))

        # For the first non-coordinate variable, copy and regrid the dataset as a whole.
        # This makes sure to correctly include the lat/lon in the regridding.
        if (not(first_var)):
            ds_regrid = ds_to_regrid[var].to_dataset() # convert data array to dataset
            ds_regrid = regridder(ds_regrid)
            first_var = True

        # Once the first variable has been included, then we can regrid by variable
        else:
            ds_regrid[var] = regridder(ds_to_regrid[var])

    print("\n")
    return(ds_regrid)
