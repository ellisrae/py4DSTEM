# Reads 4D-STEM data with hyperspy, stores as a DataCube object

import h5py
import numpy as np
from hyperspy.misc.utils import DictionaryTreeBrowser
import hyperspy.api as hs
from os.path import splitext
from process.datastructure.datacube import DataCube

def read_data(filename):
    """
    Takes a filename as input, and outputs a DataCube object.

    If filename is a .h5 file, read_data() checks if the file was written by py4DSTEM.  If it
    was, the metadata are read and saved directly.  Otherwise, the file is read with hyperspy,
    and metadata is scraped and saved from the hyperspy file.
    """
    print("Reading file {}...\n".format(filename))
    # Check if file was written by py4DSTEM
    try:
        h5_file = h5py.File(filename,'r')
        if is_py4DSTEMfile(h5_file):
            print("{} is a py4DSTEM HDF5 file.  Reading...".format(filename))
            R_Ny,R_Nx,Q_Ny,Q_Nx = h5_file['4D-STEM_data']['datacube']['datacube'].shape
            datacube = DataCube(data=h5_file['4D-STEM_data']['datacube']['datacube'].value,
                            R_Ny=R_Ny,R_Nx=R_Nx,Q_Ny=Q_Ny,Q_Nx=Q_Nx,filename=filename,
                            is_py4DSTEM_file=True, h5_file=h5_file)
            h5_file.close()
            return datacube
        else:
            h5_file.close()
    except IOError:
        pass

    # Use hyperspy
    print("{} is not a py4DSTEM file.  Reading with hyperspy...".format(filename))
    try:
        hyperspy_file = hs.load(filename)
        if len(hyperspy_file.data.shape)==3:
            R_N, Q_Ny, Q_Nx = hyperspy_file.data.shape
            R_Ny, R_Nx = R_N, 1
        elif len(hyperspy_file.data.shape)==4:
            R_Ny, R_Nx, Q_Ny, Q_Nx = hyperspy_file.data.shape
        else:
            print("Error: unexpected raw data shape of {}".format(hyperspy_file.data.shape))
            print("Initializing random datacube...")
            return DataCube(data=np.random.rand(100,512,512),
                            R_Ny=10,R_Nx=10,Q_Ny=512,Q_Nx=512,
                            filename=filename,is_py4DSTEM_file=False)
        return DataCube(data=hyperspy_file.data, R_Ny=R_Ny, R_Nx=R_Nx, Q_Ny=Q_Ny, Q_Nx=Q_Nx,
                            original_metadata_shortlist=hyperspy_file.metadata,
                            original_metadata_all=hyperspy_file.original_metadata,
                            filename=filename,is_py4DSTEM_file=False)
    except Exception as err:
        print("Failed to load", err)
        print("Initializing random datacube...")
        return DataCube(data=np.random.rand(100,512,512),R_Ny=10,R_Nx=10,Q_Ny=512,Q_Nx=512,
                        filename=None,is_py4DSTEM_file=False)


def is_py4DSTEMfile(h5_file):
    if ('version_major' in h5_file.attrs) and ('version_minor' in h5_file.attrs) and ('4D-STEM_data' in h5_file.keys()):
        return True
    else:
        return False





############################### File structure ###############################
#
# /
# |--attr: version_major=0
# |--attr: version_minor=2
# |--grp: 4D-STEM_data
#             |
#             |--grp: datacube
#             |          |--attr: emd_group_type=1
#             |          |--data: datacube
#             |          |--data: dim1
#             |          |    |--attr: name="R_y"
#             |          |    |--attr: units="[n_m]"
#             |          |--data: dim2
#             |          |    |--attr: name="R_y"
#             |          |    |--attr: units="[n_m]"
#             |          |--data: dim3
#             |          |    |--attr: name="R_y"
#             |          |    |--attr: units="[n_m]"
#             |          |--data: dim4
#             |               |--attr: name="R_y"
#             |               |--attr: units="[n_m]"
#             |
#             |--grp: processing
#             |          |--# This will contain objects created and used during processing
#             |          |--# e.g. vacuum probe, shifts from scan coils, binary masks,
#             |          |--#      convolution kernels, etc.
#             |
#             |--grp: metadata
#                        |--grp: original
#                        |   |--# Raw metadata from original files
#                        |
#                        |--grp: microscope
#                        |   |--# Acquisition parameters
#                        |   |--# Accelerating voltage, camera length, convergence angle, 
#                        |   |--# C2 aperture, spot size, exposure time, scan rotation angle,
#                        |   |--# scan shape, probe FWHM
#                        |
#                        |--grp: sample
#                        |   |--# Material, preparation
#                        |
#                        |--grp: user
#                        |   |--# Name, instituion, dept, contact email
#                        |
#                        |--grp: processing
#                        |   |--# original file name, processing perfomed - binning, cropping
#                        |   |--# Consider attaching logs
#                        |
#                        |--grp: calibration
#                        |   |--# R pixel size, K pixel size, R/K rotation offset
#                        |   |--# In case of duplicates here and in grp: microscope (e.g. pixel
#                        |   |--# sizes), quantities here are calculated from data rather than
#                        |   |--# being read from the instrument
#                        |
#                        |--grp: comments

