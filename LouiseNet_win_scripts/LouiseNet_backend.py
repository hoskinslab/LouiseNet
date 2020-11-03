from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO
import pandas as pd
import shutil
import os
import re


class PISA_Protein:
    def __init__(self, protein_name, pdb_file_path, mapping_file_path, chrome_driver_path, wanted_protein_letter, edge_list):
        self.protein_name = protein_name
        self.pdb_file_path = pdb_file_path
        self.mapping_file_path = mapping_file_path
        self.chrome_driver_path = chrome_driver_path
        self.main_interaction_file_name = protein_name + '_main_interaction.csv'
        self.detail_interaction_file_name = protein_name + '_detail_interaction.csv'
        self.wanted_protein_letter = wanted_protein_letter
        self.edge_list = edge_list

    # starts chrome driver

    def start_driver(self):
        url = 'https://www.ebi.ac.uk/pdbe/pisa/'
        driver = webdriver.Chrome(self.chrome_driver_path)
        driver.get(url)
        return (driver)

    # scrapes pisa chain interactions
    def scrape_chain_interaction(self):
        driver = self.start_driver()
        launch_pisa_button = driver.find_element_by_xpath(
            '//*[@id="pdbeSubmitButton"]/span/button')
        driver.execute_script("arguments[0].click();", launch_pisa_button)
        # upload pdb file /html/body/div[2]/div[2]/div/form/table/tbody/tr[4]/td/u/input
        coordinate_file_button = driver.find_element_by_css_selector("input[type='radio'][value='id_coorfile']")
        driver.execute_script("arguments[0].click();", coordinate_file_button)
        # upload pdb file
        driver.find_element_by_xpath(
            '//*[@id="sform"]/tbody/tr[3]/td/b/input[2]').send_keys(self.pdb_file_path)
        upload_button = driver.find_element_by_xpath(
            '//*[@id="sform"]/tbody/tr[3]/td/b/input[3]')
        driver.execute_script("arguments[0].click();", upload_button)
        # get interfaces
        interfaces_button = driver.find_element_by_xpath(
            '//*[@id="pdbeSubmitButton"]/span/button')
        driver.execute_script("arguments[0].click();", interfaces_button)
        # waiting for page to load to interfaces page
        wait = WebDriverWait(driver, 300)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//button[contains(text(), "Interfaces")]')))
        # save content into bs and taking out data table
        content = driver.page_source
        soup = bs(content, "html.parser")
        table = soup.find('table', {'class': 'data-table tborder'})
        saved_pdb = ""
        for row in table.find_all('tr'):
            pdb = ""
            for data in row.find_all('td'):
                pdb = pdb + "," + data.text.replace(u'\xa0', u'')
            saved_pdb = saved_pdb + "\n" + pdb[1:]
            # writing csv
        with open(self.main_interaction_file_name, 'w', encoding='utf-8') as f:
            f.write(saved_pdb)
        return (driver)

    # making letter edge list for chains alone
    def make_chain_edge_list(self):
        chain_only_df = pd.read_csv(
            self.main_interaction_file_name, header=None)
        # clean PISA_df
        list_to_remove = []
        list_to_move_right = []
        for i in range(len(chain_only_df)):
            if chain_only_df.iloc[i, 0] == 'Average:':
                list_to_remove.append(i)
        if (len(list_to_remove) != 0):
            chain_only_df = chain_only_df.drop([0], axis=1)
        for i in range(len(chain_only_df)):
            if str(chain_only_df.iloc[i, 0]) == 'nan':
                list_to_move_right.append(i)
        for i in range(len(list_to_move_right)):
            chain_only_df.iloc[list_to_move_right[i],
                               :] = chain_only_df.iloc[list_to_move_right[i], :].shift(1)
        for i in range(len(chain_only_df)):
            if len(str(chain_only_df.iloc[i, 2])) != 1 or len(str(chain_only_df.iloc[i, 7])) != 1:
                list_to_remove.append(i)
        chain_only_df = chain_only_df.drop(list_to_remove, axis=0)
        chain_only_df.columns = ['ID', '', 'Chain 1', 'Number of Interfacing Atoms',
                           'Number of Interfacing Residues', 'Surface Area', 'Unnamed: 6',
                           'Chain 2', 'Number of Interfacing Atoms.1', 'Unnamed: 9',
                           'Number of Interfacing Residues.1', 'Interface Area',
                           'Delta G(kal/mol)', 'Delta G (p value)', 'Number of Potential Hydrogen Bonds',
                           ' Number of Potential Salt Bridges',
                           'Number of Potential Disulfide Bonds',
                           'Complexation Significance Score']
        chain_only_df.to_csv(
            self.main_interaction_file_name, header=True, index=None)
        mapping_df = pd.read_csv(self.mapping_file_path, header=None)
        # making mapping_df with numberical mapping
        mapping_df[2] = (range(1, len(mapping_df) + 1))
        mapping_df.columns = ['Chain Name', 'Chain ID', 'Node ID']
        mapping_df.to_csv(self.protein_name + '_mapping.csv',
                          header=True, index=None)
        if self.edge_list == 'letter':
            # making letter based edgelist
            edgelist_letter_df = chain_only_df.iloc[:, [2, 7]]
            edgelist_letter_df.to_csv(
                self.protein_name + '_edgelist_chainID.csv', header=None, index=None)
        elif self.edge_list == 'name':
            # making name based edgelist
            edgelist_name_df = chain_only_df.iloc[:, [2, 7]]
            for i in range(len(mapping_df)):
                for j in range(len(chain_only_df)):
                    if chain_only_df.iloc[j, 2] == mapping_df.iloc[i, 1]:
                        edgelist_name_df.iloc[j, 0] = mapping_df.iloc[i, 0]
                    if chain_only_df.iloc[j, 7] == mapping_df.iloc[i, 1]:
                        edgelist_name_df.iloc[j, 1] = mapping_df.iloc[i, 0]
            edgelist_name_df.to_csv(
                self.protein_name + '_edgelist_chainName.csv', header=None, index=None)
        elif self.edge_list == 'number':
            # making number based edgelist
            edgelist_numeric_df = chain_only_df.iloc[:, [2, 7]]
            for i in range(len(mapping_df)):
                for j in range(len(chain_only_df)):
                    if chain_only_df.iloc[j, 2] == mapping_df.iloc[i, 1]:
                        edgelist_numeric_df.iloc[j, 0] = mapping_df.iloc[i, 2]
                    if chain_only_df.iloc[j, 7] == mapping_df.iloc[i, 1]:
                        edgelist_numeric_df.iloc[j, 1] = mapping_df.iloc[i, 2]
            edgelist_numeric_df.to_csv(
                self.protein_name + '_edgelist_nodeID.csv', header=None, index=None)

    # checking for matched residual in main interaction page and scrape detail interaction of residuals
    def scrape_residual_interaction(self):
        driver = self.scrape_chain_interaction()
        chain_and_residual_df = pd.read_csv(
            self.main_interaction_file_name, header=None)
        # clean PISA_df
        list_to_remove = []
        list_to_move_right = []
        for i in range(len(chain_and_residual_df)):
            if chain_and_residual_df.iloc[i, 0] == 'Average:':
                list_to_remove.append(i)
        if (len(list_to_remove) != 0):
            chain_and_residual_df = chain_and_residual_df.drop([0], axis=1)
        for i in range(len(chain_and_residual_df)):
            if str(chain_and_residual_df.iloc[i, 0]) == 'nan':
                list_to_move_right.append(i)
        for i in range(len(list_to_move_right)):
            chain_and_residual_df.iloc[list_to_move_right[i],
                                       :] = chain_and_residual_df.iloc[list_to_move_right[i], :].shift(1)
        chain_and_residual_df = chain_and_residual_df.drop(
            list_to_remove, axis=0)
        # finding matched ids: ids_left: matched ids on left col; ids_right: matched ids on right col
        ids_left = []
        ids_right = []
        for i in range(len(chain_and_residual_df)):
            if str(chain_and_residual_df.iloc[i, 0]) == 'nan':
                chain_and_residual_df.iloc[i,
                                           0] = chain_and_residual_df.iloc[i - 1, 0] + 1
            if (str(chain_and_residual_df.iloc[i, 2]) == self.wanted_protein_letter) and (
                    len(chain_and_residual_df.iloc[i, 7]) == 1):
                ids_left.append(chain_and_residual_df.iloc[i, 0] - 1)
            if (str(chain_and_residual_df.iloc[i, 7]) == self.wanted_protein_letter) and (
                    len(chain_and_residual_df.iloc[i, 2]) == 1):
                ids_right.append(chain_and_residual_df.iloc[i, 0] - 1)

        # creating used elements for the loop
        details_button = driver.find_element_by_xpath(
            '/html/body/div[2]/div[2]/div/form/table[2]/tbody/tr[1]/td/span[3]/span/button')
        wanted_details = pd.DataFrame()
        # looping through matched(on the left) rows and scrapping the details
        for i in ids_left:
            select_button = driver.find_element_by_xpath(
                "//input[@name='radio_interface' and @value={}]".format(i))
            details_button = driver.find_element_by_xpath(
                '//button[contains(text(), "Details")]')
            driver.execute_script("arguments[0].click();", select_button)
            driver.execute_script("arguments[0].click();", details_button)
            content = driver.page_source
            soup = bs(content, "html.parser")
            tables = soup.find_all('table', {'class': 'standard'})
            table_left = tables[len(tables) - 3]
            table_right = tables[len(tables) - 2]
            # finding left table
            saved_detail_left = ""
            for row in table_left.find_all('tr'):
                detail_left = ""
                for data in row.find_all('td'):
                    detail_left = detail_left + "," + \
                        data.text.replace(u'\xa0', u'')
                saved_detail_left = saved_detail_left + "\n" + detail_left[1:]
                # finding right table
            saved_detail_right = ""
            for row in table_right.find_all('tr'):
                detail_right = ""
                for data in row.find_all('td'):
                    detail_right = detail_right + "," + \
                        data.text.replace(u'\xa0', u'')
                saved_detail_right = saved_detail_right + \
                    "\n" + detail_right[1:]
            df_left = pd.read_csv(
                StringIO(saved_detail_left), sep=',', header=None)
            df_right = pd.read_csv(
                StringIO(saved_detail_right), sep=',', header=None)
            # saving nonezero interactions into wanted_details
            for j in range(len(df_left) - 1):
                if df_left.iloc[j, 4] != '  0.00':
                    wanted_details = wanted_details.append(df_left.iloc[j, :])
            for k in range(len(df_right) - 1):
                if df_right.iloc[k, 4] != '  0.00':
                    wanted_details = wanted_details.append(df_right.iloc[k, :])
            return_button = driver.find_element_by_xpath(
                '//button[contains(text(), "Interfaces")]')
            driver.execute_script("arguments[0].click();", return_button)
        # looping through matched(on the right) rows and scrapping the details
        for i in ids_right:
            select_button = driver.find_element_by_xpath(
                "//input[@name='radio_interface' and @value={}]".format(i))
            details_button = driver.find_element_by_xpath(
                '//button[contains(text(), "Details")]')
            driver.execute_script("arguments[0].click();", select_button)
            driver.execute_script("arguments[0].click();", details_button)
            content = driver.page_source
            soup = bs(content, "html.parser")
            tables = soup.find_all('table', {'class': 'standard'})
            table_left = tables[len(tables) - 3]
            table_right = tables[len(tables) - 2]
            # finding left table
            saved_detail_left = ""
            for row in table_left.find_all('tr'):
                detail_left = ""
                for data in row.find_all('td'):
                    detail_left = detail_left + "," + \
                        data.text.replace(u'\xa0', u'')
                saved_detail_left = saved_detail_left + "\n" + detail_left[1:]
                # finding right table
            saved_detail_right = ""
            for row in table_right.find_all('tr'):
                detail_right = ""
                for data in row.find_all('td'):
                    detail_right = detail_right + "," + \
                        data.text.replace(u'\xa0', u'')
                saved_detail_right = saved_detail_right + \
                    "\n" + detail_right[1:]
            df_left = pd.read_csv(
                StringIO(saved_detail_left), sep=',', header=None)
            df_right = pd.read_csv(
                StringIO(saved_detail_right), sep=',', header=None)
            # saving nonezero interactions into wanted_details
            for j in range(len(df_right) - 1):
                if df_right.iloc[j, 4] != '  0.00':
                    wanted_details = wanted_details.append(df_right.iloc[j, :])
            for k in range(len(df_left) - 1):
                if df_left.iloc[k, 4] != '  0.00':
                    wanted_details = wanted_details.append(df_left.iloc[k, :])
            return_button = driver.find_element_by_xpath(
                '//button[contains(text(), "Interfaces")]')
            driver.execute_script("arguments[0].click();", return_button)
        wanted_details = wanted_details.iloc[::-1]
        wanted_details = wanted_details.rename(
            columns={0: "id", 1: "structure", 2: "HSDC", 3: "ASA", 4: "BSA", 5: "G"})
        wanted_details = wanted_details.drop(['id'], axis=1)
        final_index = []
        for i in range(len(wanted_details)):
            if wanted_details.iloc[i, 0][:1] == self.wanted_protein_letter:
                final_index.append(i)
            # creat the final csv with wanted format
        detail_interaction = [[0] * 2] * len(final_index)
        detail_interaction = pd.DataFrame.from_records(detail_interaction)
        detail_interaction.iloc[0, 0] = wanted_details.iloc[0, 0][:1]
        for i in range(len(final_index)):
            detail_interaction.iloc[i,
                                    1] = wanted_details.iloc[final_index[i], 0]
        for i in range(1, len(detail_interaction)):
            if final_index[i] - final_index[i - 1] == 1:
                detail_interaction.iloc[i,
                                        0] = detail_interaction.iloc[i - 1, 0]
            else:
                detail_interaction.iloc[i,
                                        0] = wanted_details.iloc[final_index[i] - 1, 0][:1]
        return (detail_interaction)

    def make_residual_edgelist(self):
        detail_interaction_df = self.scrape_residual_interaction()
        chain_and_residual_df = pd.read_csv(
            self.main_interaction_file_name, header=None)
        list_to_remove = []
        list_to_move_right = []
        for i in range(len(chain_and_residual_df)):
            if chain_and_residual_df.iloc[i, 0] == 'Average:':
                list_to_remove.append(i)
        if (len(list_to_remove) != 0):
            chain_and_residual_df = chain_and_residual_df.drop([0], axis=1)
        for i in range(len(chain_and_residual_df)):
            if str(chain_and_residual_df.iloc[i, 0]) == 'nan':
                list_to_move_right.append(i)
        for i in range(len(list_to_move_right)):
            chain_and_residual_df.iloc[list_to_move_right[i],
                                       :] = chain_and_residual_df.iloc[list_to_move_right[i], :].shift(1)
        for i in range(len(chain_and_residual_df)):
            if len(str(chain_and_residual_df.iloc[i, 2])) != 1 or len(str(chain_and_residual_df.iloc[i, 7])) != 1:
                list_to_remove.append(i)
        chain_and_residual_df = chain_and_residual_df.drop(
            list_to_remove, axis=0)
        chain_and_residual_df.to_csv(
            self.main_interaction_file_name, header=None, index=None)
        # list 1,2 = main interaction; list 3,4 = detail interactions
        list_1 = []
        list_2 = []
        list_3 = []
        list_4 = []
        for i in range(len(chain_and_residual_df)):
            list_1.append(chain_and_residual_df.iloc[i, 2])
            list_2.append(chain_and_residual_df.iloc[i, 7])
        for i in range(len(detail_interaction_df)):
            list_3.append(detail_interaction_df.iloc[i, 0])
            list_4.append(detail_interaction_df.iloc[i, 1])
        chain_and_residual_df = pd.DataFrame()
        chain_and_residual_df['left'] = list_1 + list_3
        chain_and_residual_df['right'] = list_2 + list_4
        list_to_remove = []
        for i in range(len(chain_and_residual_df)):
            if chain_and_residual_df.iloc[i, 0] == self.wanted_protein_letter or chain_and_residual_df.iloc[i, 1] == self.wanted_protein_letter:
                list_to_remove.append(i)
        if (len(list_to_remove) != 0):
            chain_and_residual_df = chain_and_residual_df.drop(
                list_to_remove, axis=0)
        mapping_df = pd.read_csv(self.mapping_file_path, header=None)
        unique_1 = mapping_df.iloc[:, 1].unique()
        unique_2 = detail_interaction_df.iloc[:, 1].unique()
        unique_all = [*unique_1, *unique_2]
        for i in range(len(mapping_df)):
            if mapping_df.iloc[i, 1] == self.wanted_protein_letter:
                wanted_chain_name = mapping_df.iloc[i, 0]
        for i in range(len(unique_2)):
            mapping_df = mapping_df.append(
                {0: wanted_chain_name + unique_2[i].split(':')[1], 1: unique_2[i]}, ignore_index=True)
        list_to_remove = []
        for i in range(len(mapping_df)):
            if mapping_df.iloc[i, 1] == self.wanted_protein_letter:
                list_to_remove.append(i)
        mapping_df = mapping_df.drop(list_to_remove, axis=0)
        mapping_df['number'] = (range(1, len(mapping_df) + 1))
        mapping_df.to_csv(self.protein_name + '_mapping.csv',
                          header=None, index=None)
        # making letter based edgelist
        if self.edge_list == 'letter':
            edgelist_letter_df = chain_and_residual_df
            edgelist_letter_df.to_csv(
                self.protein_name + '_edgelist_chainID_with_detail.csv', header=None, index=None)
        # making name based edgelist
        elif self.edge_list == 'name':
            edgelist_name_df = chain_and_residual_df
            for i in range(len(mapping_df)):
                for j in range(len(chain_and_residual_df)):
                    if chain_and_residual_df.iloc[j, 0] == mapping_df.iloc[i, 1]:
                        edgelist_name_df.iloc[j, 0] = mapping_df.iloc[i, 0]
                    if chain_and_residual_df.iloc[j, 1] == mapping_df.iloc[i, 1]:
                        edgelist_name_df.iloc[j, 1] = mapping_df.iloc[i, 0]
            edgelist_name_df.to_csv(
                self.protein_name + '_edgelist_chainName_with_detail.csv', header=None, index=None)
        # making number based edgelist
        elif self.edge_list == 'number':
            edgelist_numeric_df = chain_and_residual_df
            for i in range(len(mapping_df)):
                for j in range(len(chain_and_residual_df)):
                    if chain_and_residual_df.iloc[j, 0] == mapping_df.iloc[i, 1]:
                        edgelist_numeric_df.iloc[j, 0] = mapping_df.iloc[i, 2]
                    if chain_and_residual_df.iloc[j, 1] == mapping_df.iloc[i, 1]:
                        edgelist_numeric_df.iloc[j, 1] = mapping_df.iloc[i, 2]
            edgelist_numeric_df.to_csv(
                self.protein_name + '_edgelist_nodeID_with_detail.csv', header=None, index=None)

    def organize_file(self, current_directory):
        final_directory = os.path.join(current_directory, self.protein_name)
        if os.path.exists(final_directory):
            final_directory = final_directory + ' copy'
            os.makedirs(final_directory)
            for filename in os.listdir(current_directory):
                filename = '/' + filename
                if filename.startswith('/' + self.protein_name + '_'):
                    shutil.move(current_directory + filename, final_directory + filename)
            os.chdir(final_directory)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
            for filename in os.listdir(current_directory):
                filename = '/' + filename
                if filename.startswith('/' + self.protein_name + '_'):
                    shutil.move(current_directory + filename, final_directory + filename)
            os.chdir(final_directory)


