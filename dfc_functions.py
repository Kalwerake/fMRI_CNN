import os
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns


class DFC:
    """
    Calculating and storing dynamic functional correlation data in .pkl format.

    Input folder should contain extracted time series data based on CC200 atlas.

    Data must be stored in BIDS format, with file extension `.1D`, tab seperated '\t' and line terminator \n

    needs:
    import os
    import pickle
    import pandas as pd """

    def __init__(self, description_df, roi_folder, pickle_folder):
        """
        description_df: (pandas DataFrame)
            pandas dataframe containing phenotypic data,
            and extracted time series data file names under column 'CC200'.
        roi_folder: (subdirectory name)
                    input folder name containing all time series data as subdirectory in main directory.
        pickle_folder:(subdirectory name)
                     subdirectory folder name for storing pickle files containing dynamic correlation data.

        """
        self.df = description_df
        # Access roi data file names
        self.roi_files = description_df['CC200']
        # subdirectory containing  roi data
        self.roi_repo = os.path.join(os.getcwd(), roi_folder)
        # subdirectory path for dfc data pickle storage
        self.pickle_repo = os.path.join(os.getcwd(), pickle_folder)
        # make subdirectory for pickle storage
        os.mkdir(self.pickle_repo)

        # all file paths for accessing ROI time series data
        self.roi_paths_all = [self.path_finder(file) for file in self.roi_files]

        self.pickle_file_all = [self.pickle_name_maker(ts) for ts in self.roi_files]  # paths to all .pkl files

        self.pickle_paths_all = [os.path.join(self.pickle_repo, file) for file in self.pickle_file_all]

    def path_finder(self, roi_data):
        """ internal method, called in __init__ to produce a list of paths for ROI time series file access"""
        roi_path = os.path.join(self.roi_repo, roi_data)

        return roi_path

    def pickle_name_maker(self, roi_file):
        """ internal method, called in __init__ to produce a list of paths for .pkl file storage"""

        location_subject = roi_file.replace('_rois_cc200.1D', '')
        pickle_file = location_subject + '_dfc.pkl'

        return pickle_file

    def fetch_roi_avg_ts(self, path):

        """ internal function for reading ROI time series data

        """
        df_time = pd.read_csv(path, sep='\t', lineterminator='\n')

        return df_time

    def dfc_calculator(self, time_series_data):
        """
        time_series_data: (pandas DataFrame)
                        Pandas dataframe containing time series data
        """

        dfc = {}  # dict object stores all calculated correlation data one subject at a time, key is time window number
        for i in range(len(time_series_data)):
            if (i + 22) <= len(time_series_data):  # keep window within index
                dfc[i + 1] = time_series_data.iloc[i:i + 22].corr()  # move window by 1 step
            else:
                break

        return dfc

    def pickle_recipe(self, pickle_path, dfc):
        """
        pickle_path: (pathname)
            desired path for pickle dump
        dfc: (dictionary)
            dictionary containing dynamic functional correlation data, with keys as time window number and
            correlation data as values.

        """

        with open(pickle_path, 'wb') as handle:
            pickle.dump(dfc, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def pickle_jar(self):
        """
        call pickle_jar() method for extraction of DFC data and storage in .pkl format, no arguments needed.
        """

        for i, roi_path in enumerate(self.roi_paths_all):  # take index and value of list roi_paths_all containing
            # path names for all time series data
            ts_df_raw = self.fetch_roi_avg_ts(roi_path)  # fetch time series data
            if len(ts_df_raw) >= 116:  # exclude all data with less than 116 time points
                ts_df = ts_df_raw.iloc[5:116, :]  # exclude first 5 time points and use only upto 116
                ts_df.reset_index(drop=True, inplace=True)  # reset_index to 0 for easier indexing

            else:
                continue

            dfc_dict = self.dfc_calculator(ts_df)  # calculate dynamic correlation data

            self.pickle_recipe(self.pickle_paths_all[i],
                               dfc_dict)  # store dict object in .pkl format at path in pickle_paths_all


class PickPickle:
    """
        obtain dict object containing DFC data for a subject spec
        pickle_folder: (str)
                name of subdirectory containing .pkl files """

    def __init__(self, pickle_folder):
        self.pickle_repo = os.path.join(os.getcwd(), pickle_folder)

    def get_pickle(self, dict_name):
        """dict_name: (filename.pkl)
                    .pkl filename containing DFC data

        """
        pickle_path = os.path.join(self.pickle_repo, dict_name)

        with open(pickle_path, 'rb') as f:
            loaded_dict = pickle.load(f)

        return loaded_dict


class PictureThis:

    def __init__(self, pickle_folder, fig_folder):
        self.main_dir = os.getcwd()
        self.pickle_repo = os.path.join(self.main_dir, pickle_folder)
        self.fig_repo = os.path.join(self.main_dir, fig_folder)

        os.mkdir(self.fig_repo)

    def get_pickle(self, pickle_file):
        """dict_name: (filename.pkl)
                    .pkl filename containing DFC data

        """
        pickle_path = os.path.join(self.pickle_repo, pickle_file)

        with open(pickle_path, 'rb') as f:
            loaded_dict = pickle.load(f)

        return loaded_dict

    def matrix_make(self, pickle_file):
        location_subject = pickle_file.replace('_dfc.pkl', '')
        subject_dump_repo = os.path.join(self.fig_repo, location_subject)
        os.mkdir(subject_dump_repo)
        subject_dfc_data = self.get_pickle(pickle_file)

        for i, key in enumerate(subject_dfc_data):
            subject_file = location_subject + f'_{key}.png'
            subject_fig_path = os.path.join(subject_dump_repo, subject_file)

            plt.figure(figsize=(10, 10))
            sns.heatmap(subject_dfc_data[key], annot=False, center=0, xticklabels=False, yticklabels=False, cbar=False)
            plt.savefig(subject_fig_path)
            plt.close()
