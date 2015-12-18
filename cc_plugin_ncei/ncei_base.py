#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
compliance_checker.glider_dac

Compliance Test Suite for the IOOS National Glider Data Assembly Center
https://github.com/ioos/ioosngdac/wiki
'''

from compliance_checker.base import BaseCheck, BaseNCCheck, Result
import cf_units
import numpy as np
from collections import OrderedDict
from uuid import UUID
import re



class NCEIVariable:
    def __init__(self, nc_variable, nc):
        self.ncvar = nc_variable
        self.parent_ds = nc
        # gives a number of required variables
        # valid dict keys include 'required', true or false or a function.  This
        # key is required
        # which will return true or false when evaluated,
        # weight- an integer value which will be tallied.  This key is required
        # valid_ids, a singleton value or list of values to select from,
        # (optional)
        # or a function taking a value which returns whether a value is valid
        # type_fn:  a typechecking function # NOT IMPLEMENTED YET
        # alt_name: an alternate name for the variable
        self.vardata = {'long_name': {'required': False, 'weight': BaseCheck.MEDIUM},
                        'comment': {'required': False, 'weight': BaseCheck.LOW}}

    def run_checks(self):
        possible_score = total_score = 0
        #varattrs = self.vardata.get_attrs()
        missing_required = []
        failing_vals = {}
        for k, d in self.vardata.iteritems():
            att_val = getattr(self.vardata, k, None)
            # Whether an attribute is required or not should always be present
            # would try catch be more idiomatic
            import ipdb; ipdb.set_trace()
            if hasattr(d['required'], '__call__'):
                req_stat = d['required']()
            else:
                req_stat = d['required']
            if req_stat:
                possible_score += d['weight']
                if att_val is None:
                    missing_required.append(k)

            if 'valid_ids' in d:
                msg = None
                try:
                    is_valid_val = att_val in d['valid_ids']
                    #rtn_vals = "Val not in " + str(d['valid_ids'])
                except TypeError:
                    # function
                    if hasattr(d['valid_ids'], '__call__'):
                        is_valid_val, msg = d['valid_ids'](att_val)
                    else:
                        is_valid_val = att_val == d['valid_ids']
                if not is_valid_val:
                    # if we ran a function, it should return a message.
                    # otherwise cast the list to string
                    if msg:
                        failing_vals[k] = msg
                    else:
                        failing_vals[k] = "{} not in {}".format(att_val,
                                                            list(d['valid_ids']))

    def check_ancillary_vars(self, anc_vars):
        """Checks that the referenced ancillary variables actually exist
           in the dataset"""
        anc_var_set = set(anc_vars.split(' '))
        invalid_vars = anc_var_set - set(ds.variables)
        return True, None if returnstat else False, invalid_vars.join(', ')



class NCEICoordVar(NCEIVariable):
    def __init__(self):
        self.vardata = super.vardata
        self.vardata.extend(
          OrderedDict(
            # TODO: Make a mutually dependent check based on the name of the
            # variable
            'standard_name', {'required': True, 'weight': BaseCheck.HIGH,
                              'valid_ids': {'longitude', 'latitude', 'depth', 'pressure'}},
            'long_name', {'required': False, 'weight': BaseCheck.MEDIUM},
            'axis', {'required': True, 'weight': BaseCheck.HIGH,
                       'valid_ids': axis_matches},
            'valid_min', {'required': False, 'weight': BaseCheck.MEDIUM},
            'valid_max', {'required': False, 'weight': BaseCheck.MEDIUM},
            'ancillary_variables', {'required': False,
                                    'weight': BaseCheck.MEDIUM,
                                    'valid_ids': self.check_ancillary_vars},
          ))


        def axis_matches(self, axis_val):
            #if axis_val not in {'X', 'Y', 'Z'}:
            expect = None
            if axis_val == 'X':
                expect = {'longitude'}
            elif axis_val == 'Y':
                expect = {'latitude'}
            elif axis_val == 'Z':
                # 'Usually "depth" or "altitude" is used'.  Whitelist?
                expect = {'depth', 'altitude', 'height'}
            else:
                return (False, "Invalid axis value '{}'".format(axis_val))

            if self.ncvar.standard_name in expect:
                return (True, None)
            else:
                std_mismatch = "Expected standard names: {}, " \
                               "got standard name {}".format(expect,
                                                       self.ncvar.standard_name)
                return (False, std_mismatch)

class NCEIPhysVar(NCEIVariable):
    {'long_name', {'required': False, 'weight': BaseCheck.MEDIUM},
     'standard_name', {'required': False, 'weight': BaseCheck.MEDIUM},
     'standard_name', {'required': False, 'weight': BaseCheck.MEDIUM},
    }

    def check_nodc_template_version(self, ds):
        # TODO: complete template list
        template_versions = {'NODC_Point_Template_v1.1',
          'NODC_NetCDF_TimeSeries_Orthogonal_Template_v1.1',
          'NODC_NetCDF_TimeSeries_Incomplete_Template_v1.1',
          'NODC_NetCDF_Trajectory_Template_v1.1',
          'NODC_NetCDF_Profile_Orthogonal_Template_v1.1',
          'NODC_NetCDF_Profile_Incomplete_Template_v1.1',
          'NODC_NetCDF_TimeSeriesProfile_Orthogonal_Template_v1.1',
          'NODC_NetCDF_TimeSeriesProfile_IncompleteVertical_OrthogonalTemporal_Template_v1.1',
          'NODC_NetCDF_TimeSeriesProfile_OrthogonalVertical_IncompleteTemporal_Template_v1.1',
          'NODC_NetCDF_TimeSeriesProfile_Incomplete_Template_v1.1',
          'NODC_NetCDF_TrajectoryProfile_Orthogonal_Template_v1.1',
          'NODC_NetCDF_TrajectoryProfile_Incomplete_Template_v1.1',
          'NODC_NetCDF_Grid_Template_v1.1'}
        nodc_template_version = (getattr(None, 'nodc_template_version', None)
                                 in template_versions)


    def check_valid_uuid(self, ds):
        """
        Checks that there exists a UUID attribute and that it is properly formed
        """
        uuid = getattr(None, 'nodc_template_version', None)
        if uuid is not None:
            try:
                uuid = UUID(uuid)
            except ValueError:
                # TODO: add result here
                return Result(BaseCheck.MEDIUM, (0, 1), 'check_valid_uuid',
                              ['Improperly formed UUID'])
            else:
                return Result(BaseCheck.MEDIUM, (1, 1), 'check_valid_uuid')
        else:
            return Result(BaseCheck.MEDIUM, (1, 1), 'check_valid_uuid')


    def check_sea_name(self, ds):
        df = pd.read_csv('https://www.nodc.noaa.gov/General/NODC-Archive/seanamelist.txt',
                        sep=r'\s{2,}', skiprows=[0,1,2,3,4,5,6,8])
        sea_name = getattr(None, 'sea_name', None)
        is_in_names = df['Sea Name'].str.contains(sea_name).any()


#
#
#class NCEITimeSeries(BaseNCCheck):
#    register_checker = True
#    name = 'ncei-timeseries'
#
#    @classmethod
#    def beliefs(cls):
#        '''
#        Not applicable for gliders
#        '''
#        return {}
#
#    @classmethod
#    def make_result(cls, level, score, out_of, name, messages):
#        return Result(level, (score, out_of), name, messages)
#
#    def setup(self, ds):
#        pass
#
#
#    def check_time_required(self, ds):
#        '''
#        '''
#        level = BaseCheck.HIGH
#        out_of = 4
#        score = 0
#        messages = []
#
#        if 'time' in ds.dataset.variables:
#            score += 1
#        else:
#            messages.append("Variable time is missing and all supporting attributes")
#            return self.make_result(level, score, out_of, 'Verifies time exists and is valid', messages)
#
#        variable = ds.dataset.variables['time']
#
#        if getattr(variable, "standard_name", None) == 'time':
#            score += 1
#        else:
#            messages.append("Invalid standard_name for time")
#
#        # Calendar is required if it's not default which is gregorian
#        calendar = getattr(variable, "calendar", None)
#        # Valid calendars come from CF 1.6 §4.4.1
#        valid_calendars = ('gregorian', 'standard', 'proleptic_gregorian', 'noleap', '365_day', 'all_leap', '366_day', 'julian', 'none')
#        if calendar is None or calendar.lower() in valid_calendars:
#            score += 1
#        else:
#            messages.append("time has an invalid calendar: %s" % calendar)
#
#        if getattr(variable, 'axis', None) == 'T':
#            score += 1
#        else:
#            messages.append("time must define axis to be equal to 'T'")
#
#
#        return self.make_result(level, score, out_of, 'Verifies time exists and is valid', messages)


