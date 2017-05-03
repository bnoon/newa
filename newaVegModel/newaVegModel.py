#!/usr/local/bin/python

import sys, imp
from mx import DateTime
from print_exception import print_exception
import newaVegModel_io
import newaCommon.newaCommon_io
from newaCommon.newaCommon import *

class program_exit (Exception):
	pass

# import the dictionarey containing information about the specified veg pest (assumes sys and imp have already been imported)
def import_info_dict(pest):
	if pest in newaVegModel_io.disease_dict:
		name = pest + '_info_dict'
	else:
		return None
	try:
		file, pathname, description = imp.find_module(name,['newaVegModel'])
		pmd = imp.load_module(name, file, pathname, description)
		return pmd.pest_status_management
	except:
		print_exception()
		return None
	
#--------------------------------------------------------------------------------------------		
class Crucifer (Base):
	#--------------------------------------------------------------------------------------------	
	#   fill stage-dependent portions of summary dictionary
	def filldict (self, psmk, k, tech_choice, smry_dict):
		try:
			smry_dict['stage']  = k
			smry_dict['status'] = psmk['status']
			smry_dict['manage'] = psmk['management_oc']
			if tech_choice == 'organic':
				smry_dict['manage'] += psmk['management_o']
			else:
				smry_dict['manage'] += psmk['management_c']
			if psmk.has_key('pesticide_link'):
				smry_dict['manage'] += '<a href="%s" target="_blank">Pesticide information</a>' % (psmk['pesticide_link'])
		except:
			print_exception()
		return smry_dict
		
	#--------------------------------------------------------------------------------------------	
	#   main crucifer model routine
	def run_crucifer_disease(self, stn, pest, accend, tech_choice, output):
		try:
			smry_dict = {}
			smry_dict['pest'] = pest
			if not accend:
				accend = DateTime.now()
			smry_dict['output'] = output
			if output == 'standalone':
				smry_dict['stn'] = stn
				smry_dict['accend'] = accend

			# determine information needed for particular disease
			pest_status_management = import_info_dict(pest)
			if not pest_status_management:
				return newaCommon_io.errmsg('A model is not available for the disease you selected.')
			smry_dict['pest_name'] = pest_status_management['pest_name']
			smry_dict['crop_stages'] = pest_status_management['messages'].keys()
			
			# get station name - don't need this for Crucifers
			# ucanid,smry_dict['station_name'] = get_metadata (stn)

			# get status and recommendations
			smry_dict['stage']  = "Not defined"
			smry_dict['status'] = "Not defined"
			smry_dict['manage'] = "Not defined"
			for k in smry_dict['crop_stages']:
				psmk = pest_status_management['messages'][k]
				if psmk.has_key('datelo'):
					datelo = DateTime.DateTime(accend.year,*psmk['datelo'])
					datehi = DateTime.DateTime(accend.year,*psmk['datehi'])
					if accend >= datelo and accend <= datehi:
						smry_dict = self.filldict(psmk,k,tech_choice,smry_dict)
						break
			else:
				# didn't fall within any date ranges; now get dd values and check dd ranges
				start_date_dt = DateTime.DateTime(accend.year,1,1)
				daily_data, station_name = self.get_daily (stn, start_date_dt, accend)
				smry_dict['station_name'] = station_name
				if len(daily_data) > 0:
					degday_data = self.degday_calcs (daily_data,start_date_dt,accend,'dd4c','accum')
					if len(degday_data) > 0 and degday_data[-1][4] != miss:
						ddaccum = degday_data[-1][4]
						for k in smry_dict['crop_stages']:
							psmk = pest_status_management['messages'][k]
							if psmk.has_key('ddlo'):
								if ddaccum >= psmk['ddlo'] and ddaccum <= psmk['ddhi']:
									smry_dict = self.filldict(psmk,k,tech_choice,smry_dict)
									break
						else:
							print "Error determining recommendations:",pest,stn,accend
					else:
						return self.nodata(stn, station_name, start_date_dt, accend)
				else:
					return self.nodata(stn, station_name, start_date_dt, accend)
				
			return newaVegModel_io.crucifer_results(smry_dict)
		except:
			print_exception()

	#--------------------------------------------------------------------------------------------		
	#	perform crucifer output page update
	def run_crucifer_update (self,pest,altref,tech_choice):
		try:
			smry_dict = {}
			# determine information needed for calculations for particular disease
			pest_status_management = import_info_dict(pest)
			if not pest_status_management:
				return newaCommon_io.errmsg('A model is not available for the disease you selected.')
			if pest_status_management['messages'].has_key(altref):
				psmk = pest_status_management['messages'][altref]
				smry_dict['crop_stages'] = pest_status_management['messages'].keys()
				smry_dict = self.filldict(psmk,altref,tech_choice,smry_dict)
			else:
				smry_dict['stage']  = "Not defined"
				smry_dict['status'] = "Not defined"
				smry_dict['manage'] = "Not defined"
			return newaVegModel_io.crucifer_sm_table(smry_dict)
		except:
			print_exception()

	#--------------------------------------------------------------------------------------------		
	#	build crucifer help page
	def run_crucifer_help (self,pest,tech_choice):
		try:
			pest_status_management = import_info_dict(pest)
			if pest_status_management:
				key_char = pest_status_management['keychar_oc']
				if tech_choice == 'organic':
					key_char += pest_status_management['keychar_o']
				else:
					key_char += pest_status_management['keychar_c']
				help_links = [(key_char,"")]
				for htup in pest_status_management['help_links']:
					help_links.append(htup)
				return newaVegModel_io.helppage(help_links)
			else:
				return newaCommon_io.errmsg('Help is not available for the disease you selected.')
		except:
			print_exception()


##### DIRECTORS #####
#--------------------------------------------------------------------------------------------					
def process_update (request,path):
	try:
		pest = None
		altref = None
		tech_choice = 'conventional'
#	 	retrieve input
		newForm = {}
		for k,v in request.form.items() :
			newForm[str(k)] = str(v)
		request.form = newForm
		if path is None:
			if request and request.form:
				try:
					if request.form.has_key('pest'): pest = request.form['pest']
					if request.form.has_key('altref'): altref = request.form['altref']
					if request.form.has_key('tech_choice'): tech_choice = request.form['tech_choice']
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		else:
			return newaCommon_io.errmsg('Error processing input')
			
# 		send input to appropriate routine
		if pest and altref:
			return Crucifer().run_crucifer_update(pest,altref,tech_choice)
		else:
			return newaCommon_io.errmsg('Error processing input')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing input')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')

#--------------------------------------------------------------------------------------------					
def process_help (request,path):
	try:
		smry_type = None
		pest = None
		tech_choice = 'conventional'
#	 	retrieve input
		newForm = {}
		for k,v in request.form.items() :
			newForm[str(k)] = str(v)
		request.form = newForm
		if path is None:
			if request and request.form:
#				print 'update form:',request.form
				try:
					smry_type = request.form['type'].strip()
					if request.form.has_key('pest'): pest = request.form['pest']
					if request.form.has_key('tech_choice'): tech_choice = request.form['tech_choice']
				except:
					print_exception()
					raise program_exit('Error processing help form')
			else:
				return newaCommon_io.errmsg('Error processing help form; check input')
		elif path[0] in ['crucifer_disease']:
			try:
				smry_type = path[0]
				pest = path[1]
			except IndexError:
				raise program_exit('Error processing help form - index error')
			except:
				print_exception()
				raise program_exit('Error processing help form')
		else:
			try:
				smry_type = path[0]
				pest = path[0]
			except IndexError:
				raise program_exit('Error processing help form - index error')
			except:
				print_exception()
				raise program_exit('Error processing help form')
			
# 		send input to appropriate routine
		if pest:
			return Crucifer().run_crucifer_help(pest,tech_choice)
		else:
			return newaCommon_io.errmsg('Error processing help input')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing help input')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error processing help')

#--------------------------------------------------------------------------------------------					
def process_input (request,path):
	try:
		stn = None
		accend = None
		pest = None
		tech_choice = "conventional"
		output = "tab"
#	 	retrieve input
		newForm = {}
		for k,v in request.form.items() :
			newForm[str(k)] = str(v)
		request.form = newForm
		if path is None:
			if request and request.form:
#				print 'form',request.form
				try:
					smry_type = request.form['type'].strip()
					if request.form.has_key('stn'):    stn = request.form['stn'].strip()
					if request.form.has_key('pest'):   pest = request.form['pest']
					if request.form.has_key('tech_choice'): tech_choice = request.form['tech_choice']
					if request.form.has_key('output'): output = request.form['output']
					if request.form.has_key('accend'):
						try:
							mm,dd,yy = request.form['accend'].split("/")
							accend = DateTime.DateTime(int(yy),int(mm),int(dd),23)
						except:
							accend = None
				except:
					print_exception()
					raise program_exit('Error processing request')
			else:
				return newaCommon_io.errmsg('Error processing form; check input')
		elif path[0] in ['crucifer_disease']:
#			print 'path:',path
			try:
				smry_type = path[0]
				pest = path[1]
				if len(path) > 2: stn = path[2]
				output = "standalone"
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
		else:
#			print 'path:',path
			try:
				smry_type = path[0]
				pest = path[0]
				if len(path) > 1: stn = path[1]
				output = "standalone"
			except IndexError:
				raise program_exit('Error processing request - index error')
			except:
				print_exception()
				raise program_exit('Error processing request')
			
# 		send input to appropriate routine
		if pest:
			return Crucifer().run_crucifer_disease(stn,pest,accend,tech_choice,output)
		else:
			return newaCommon_io.errmsg('Error processing form; check disease')
	except program_exit,msg:
		print msg
		return newaCommon_io.errmsg('Error processing form; check input')
	except:
		print_exception()
		return newaCommon_io.errmsg('Unexpected error')

