# Thesis - Exploring Machine Learning techniques for Anomaly Detection in the OAM layer in Smart Cities

## Details
Author: Jeff Geudens  
Academic year: 2018-2019  
Promotor: Luc Vandeurzen(Groep T)  
Co-promotor: Stefan Lefevre(Imec)  
University: KU Leuven, Groep T, Electronics-IT:Option Intelligent Computing  

## Contents
This GitHub folder contains the code that was used to explore two use case.
  1. Case 1 - Smart Lighting
    1. Data collection and merging
    2. Data exploration
    3. Low pass filtering
    4. Battery voltage prediction using Regression
    5. Battery voltage prediction using LSTM
  2. Case 2 - Bel-Air
    1. Data collection air quality sensors
    2. Data exploration
    3. Geospatial visualisation
    4. Anomaly detection

## Abstract
According to the latest publication of the United Nations (2018), today 55\% of the world's population lives in urban areas. By 2050, it is expected that this share will increase to 68\% or 6.0 billion people. These figures show clearly that the world is urbanising at a fast rate. The significant increase in urban population will increase the demand for energy, mobility, water, waste management and other urban services. These trends are converging at a time where a new trend is emerging: digitalisation. Our world is getting digitalised at an ever increasing pace. All the everyday objects that we use are becoming connected and 'smarter', helping us to gather more data and optimise processes. It is the combination of challenges and opportunities in cities and these new technologies that led to the rise of 'smart cities'. 

Also here in Belgium, smart city initiatives are taking off. On January 1, 2017 Flemish Minister for Internal Affairs Liesbeth Homans kicked off the "Smart Flanders-program", a 3-year research programme executed by Imec researchers. Through its living lab, IoT and smart city expertise, Imec is working on and supports major projects including "City of Things". This is a project that brings the Internet of Things to the city of Antwerp, turning it into an IoT living lab as well as a real-time open data platform by positioning smart sensors and wireless gateways at carefully selected locations, from streets to buildings. The aim is to become a European reference in smart city research, demonstrating what tomorrow's smart cities could look like and to create some guidelines and best practices for cities when transitioning towards a smart city.

One of the main issues related to smart cities (and in general for large IoT systems) is the monitoring of all the different subsystems. For smaller systems, this can be done manually or through the use of manually specified rules. However for larger systems, this approach can become insufficient. The introduction of automatic anomaly detection algorithms can be part of the solution to the monitoring problem. For large data sets, machine learning techniques can be used to do anomaly detection since they can process huge amounts of data but also discover correlations that would not be found with only manual processing. 

This thesis shows the architecture of 'City of Things' in Antwerp. One of the two cross-cutting layers is the Operations, Administration and Maintenance layer (OAM) where the monitoring of the different subsystems can be implemented. A lot of different anomaly detection techniques exist and have to be selected based on the available data and the type of business issue. Two different cases are studied while using the CRISP-DM method.

The first case that is handled is with respect to the 'Smart Lighting' project, currently being carried out in Antwerp. It was noticed that a particular sound sensor no longer worked due to a failing battery pack. The purpose of this case was to investigate models that could detect the anomalies in the battery pack. The main problem in this case is the limited amount of data: only one faulty battery pack and two normally working battery packs are available. For the purpose of this case, data was collected from the battery packs (such as the voltage) and from a weather station (such as the light intensity). After collecting and exploring the data, four different algorithms are tested: low pass filter, 'Time Series Anomaly Detection' module of Microsoft Azure's Machine Learning Studio, Regression techniques and Long-Short Term Memory. The low pass filter is able to detect anomalies where expected. This is a very simple algorithm but has some disadvantages as well such as not being able to adapt to changing settings. The anomaly detection module of Microsoft does not perform very well in this case. Regression and LSTM are used to predict the normal behaviour of a battery pack by training them on the normally working packs. This is a form of semisupervised learning where the algorithms are trained on normal data and anomalies are flagged if the real behaviour is too far off. Unfortunately, these two algorithms are not able to predict the normal behaviour with the available data and hence no anomaly detection was possible. The low pass filter is implemented in a prototype dashboard which makes it possible to change the parameter values of this model in order to show its possibilities.

The second case is linked to the Bel-Air project of which the purpose is to monitor the air quality in Antwerp with air quality sensors that are mounted on vans of the Belgian post. This case focusses on detecting whether the times between two packets for a certain sensor(inter packet times(IPT)) were considered to be normal or not. This time is linked to the spreading factor (SF) which is linked to the LoRa network quality. For this case two separate data sets are used: a metadata set and the sensor values. This metadata set is not a complete data set as it has huge gaps. To calculate the real times between two packets, these two data sets are merged. The missing values for the sensor data points after merging (spreading factor and GPS location) is not filled up since there is no way to do this reliably. After the merging, the inter packet times are calculated. In order to find out what normal inter packet times are for each spreading factor, two anomaly detection methods are tested: a static threshold and an unsupervised anomaly detection method called DBSCAN. The static threshold is set to values so that 99\% of the data is retained. This method is able to identify most peaks in the IPTs although not all of them. This is because these data points did not have any SF and hence could not be tested by the model. DBSCAN clusters the data points and marks the points that do not belong to a cluster as anomalies. This method identifies approximately half of the anomalies that the static threshold identifies. The main problem in this case is the lack of metadata for all the sensor values. These could have a beneficial impact on training the algorithm. 

It can be concluded that anomaly detection algorithms have a very big potential in monitoring smart city subsystems but that the proper data is needed for each use case. In order to make the implementation of these algorithms more successful, application developers and hardware developers should work with machine learning experts from the start to think about which parameters could be of use. Both use cases that were investigated lacked data so perhaps in a year or two, the models could be revaluated and retrained. 

\textbf{Keywords}: Anomaly detection, CRISP-DM, Data analysis, Machine learning, OAM, Smart City

