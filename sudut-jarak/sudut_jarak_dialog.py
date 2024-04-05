# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SudutJarakDialog
                                 A QGIS plugin
 Pengambaran Sudut dan Jarak
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-10-11
        git sha              : $Format:%H$
        copyright            : (C) 2021 by RM Corporation
        email                : adrianhokas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import math

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry, QgsPointXY
from qgis.utils import iface


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sudut_jarak_dialog_base.ui'))


class SudutJarakDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=iface.mainWindow()):
        """Constructor."""
        super(SudutJarakDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.iface = iface
        self.setupUi(self)

        # menghubungkan tombol Plot! dengan suatu method
        self.plot.clicked.connect(self.input_hitung)
        self.plot.clicked.connect(self.main_program)

        #definisi antarmuka
        self.iface = iface

        # array untuk menyimpan data koordinat inputan
        self.inputan = []

        # array untuk menyimpan data koordinat hitungan
        self.hitungan = []


    def main_program(self):
        a = len(self.inputan)
        
        if self.plotting_checkbox.isChecked():
            if a == 1:
                # gambar titik inputan pertama
                i = self.inputan[a-1]
                x = i[0]
                y = i[1]
                self.buat_titik(x, y)

                # gambar titik hitungan pertama
                n = self.hitungan[a-1]
                x1 = n[0]
                y1 = n[1]
                self.buat_titik(x1, y1)
            else:
                # gambar titik inputan 
                i = self.inputan[a-1]
                x = i[0]
                y = i[1]

                # gambar titik hitungan
                n = self.hitungan[a-1]
                x1 = n[0]
                y1 = n[1]
                self.buat_titik(x1, y1)
        else:
            # gambar titik inputan 
            i = self.inputan[a-1]
            x = i[0]
            y = i[1]
            self.buat_titik(x, y)

            # gambar titik hitungan
            n = self.hitungan[a-1]
            x1 = n[0]
            y1 = n[1]
            self.buat_titik(x1, y1)

        if self.garis_checkbox.isChecked():
            i = self.hitungan[a-1]
            x = i[0]
            y = i[1]

            n = self.inputan[a-1]
            x1 = n[0]
            y1 = n[1]

            self.buat_garis(x, y, x1, y1)
        

    def input_hitung(self):
        # pengaturan apabila pengguna menuliskan selain angka
        try:
            x = float(self.input_x.text())
            y = float(self.input_y.text())
            jarak = float(self.input_jarak.text())
            az = math.radians(float(self.input_az.text()))
        except Exception as e:
            print('X, Y, Jarak, dan Azimuth Yang Diinputkan harus berupa angka')
        
        # conditional statement X dan Y terbalik
        if (x > y):
            raise Exception('Nilai koordinat X dan Y yang anda masukkan terbalik.')
        
        # conditional statement azimuth bernilai negatif
        if (az < 0):
            raise Exception ('Azimuth Yang Diinput Tidak Boleh Bernilai Negatif.')
            
        # conditional statement azimuth lebih dari 360
        while (az > 360):
            az -= 360
            
        # conditional statement jarak bernilai negatif
        if (jarak < 0):
            raise Exception('Jarak Yang Diinput Tidak Boleh Bernilai Negatif.')
        
        # conditional statement jarak tidak boleh melebihi batas kelengkungan bumi
        if (jarak > 37000):
            raise Exception('Jarak Yang Diinput Melebihi Batas Kelengkungan Bumi.')
        
        if self.plotting_checkbox.isChecked():
            try:
                a = len(self.inputan)
                i = self.hitungan[a-1]
                x = i[0]
                y = i[1]
            except Exception as e:
                print('Plotting Secara Continues Hanya Bisa Apabila Sudah Diinputkan Minimal Satu Titik.')
 
        
        # menghitung koordinat titik baru berdasarkan inputan jarak dan azimuth
        x1 = (jarak * math.sin(az)) + x
        y1 = (jarak * math.cos(az)) + y
        
        # menyimpan data inputan dan hitungan ke array
        xy = [x,y]
        x1y1 = [x1,y1]

        self.inputan.append(xy)
        self.hitungan.append(x1y1)

        

    def buat_titik(self, x, y):
        # input epsg
        inputepsg = str(self.input_epsg.currentText())
        epsg = "Point?crs=EPSG:" + inputepsg
        
        # mendefinisikan sistem proyeksi dan membuat layer pada memory
        layer = QgsVectorLayer(epsg, "Plot Titik", "memory")
        QgsProject.instance().addMapLayer(layer)

        # memberi geometri titik pada fitur baru
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))

        # menambahkan fitur pada layer
        layer.dataProvider().addFeatures([feature])
        layer.updateExtents()

        # zoom ke layer
        self.iface.actionZoomToLayer().trigger()
    
    
    def buat_garis(self, x, y, x1, y1):
        # input epsg
        inputepsg = str(self.input_epsg.currentText())
        epsg = "LineString?crs=EPSG:" + inputepsg
        
        # mendefinisikan sistem proyeksi dan membuat layer pada memory
        layer = QgsVectorLayer(epsg, "Plot Garis", "memory")
        QgsProject.instance().addMapLayer(layer)

        # mendefinisikan  garis
        line_start = QgsPointXY(x1,y1)
        line_end = QgsPointXY(x,y)

        # memberi geometri garis pada fitur baru
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolylineXY([line_start, line_end]))

        # menambahkan fitur pada layer
        layer.dataProvider().addFeatures([feature])
        layer.updateExtents()



