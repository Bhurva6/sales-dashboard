'use client';

import React, { useState, useMemo } from 'react';

// India state coordinates (approximate centers for pins)
const INDIA_STATE_COORDS: Record<string, { lat: number; lng: number; name: string }> = {
  'ANDHRA PRADESH': { lat: 15.9129, lng: 79.7400, name: 'Andhra Pradesh' },
  'ARUNACHAL PRADESH': { lat: 28.2180, lng: 94.7278, name: 'Arunachal Pradesh' },
  'ASSAM': { lat: 26.2006, lng: 92.9376, name: 'Assam' },
  'BIHAR': { lat: 25.0961, lng: 85.3131, name: 'Bihar' },
  'CHHATTISGARH': { lat: 21.2787, lng: 81.8661, name: 'Chhattisgarh' },
  'GOA': { lat: 15.2993, lng: 74.1240, name: 'Goa' },
  'GUJARAT': { lat: 22.2587, lng: 71.1924, name: 'Gujarat' },
  'HARYANA': { lat: 29.0588, lng: 76.0856, name: 'Haryana' },
  'HIMACHAL PRADESH': { lat: 31.1048, lng: 77.1734, name: 'Himachal Pradesh' },
  'JHARKHAND': { lat: 23.6102, lng: 85.2799, name: 'Jharkhand' },
  'KARNATAKA': { lat: 15.3173, lng: 75.7139, name: 'Karnataka' },
  'KERALA': { lat: 10.8505, lng: 76.2711, name: 'Kerala' },
  'MADHYA PRADESH': { lat: 22.9734, lng: 78.6569, name: 'Madhya Pradesh' },
  'MAHARASHTRA': { lat: 19.7515, lng: 75.7139, name: 'Maharashtra' },
  'MANIPUR': { lat: 24.6637, lng: 93.9063, name: 'Manipur' },
  'MEGHALAYA': { lat: 25.4670, lng: 91.3662, name: 'Meghalaya' },
  'MIZORAM': { lat: 23.1645, lng: 92.9376, name: 'Mizoram' },
  'NAGALAND': { lat: 26.1584, lng: 94.5624, name: 'Nagaland' },
  'ODISHA': { lat: 20.9517, lng: 85.0985, name: 'Odisha' },
  'PUNJAB': { lat: 31.1471, lng: 75.3412, name: 'Punjab' },
  'RAJASTHAN': { lat: 27.0238, lng: 74.2179, name: 'Rajasthan' },
  'SIKKIM': { lat: 27.5330, lng: 88.5122, name: 'Sikkim' },
  'TAMIL NADU': { lat: 11.1271, lng: 78.6569, name: 'Tamil Nadu' },
  'TELANGANA': { lat: 18.1124, lng: 79.0193, name: 'Telangana' },
  'TRIPURA': { lat: 23.9408, lng: 91.9882, name: 'Tripura' },
  'UTTAR PRADESH': { lat: 26.8467, lng: 80.9462, name: 'Uttar Pradesh' },
  'UTTARAKHAND': { lat: 30.0668, lng: 79.0193, name: 'Uttarakhand' },
  'WEST BENGAL': { lat: 22.9868, lng: 87.8550, name: 'West Bengal' },
  'DELHI': { lat: 28.7041, lng: 77.1025, name: 'Delhi' },
  'JAMMU AND KASHMIR': { lat: 33.7782, lng: 76.5762, name: 'Jammu & Kashmir' },
  'LADAKH': { lat: 34.1526, lng: 77.5771, name: 'Ladakh' },
  'PUDUCHERRY': { lat: 11.9416, lng: 79.8083, name: 'Puducherry' },
  'CHANDIGARH': { lat: 30.7333, lng: 76.7794, name: 'Chandigarh' },
  'ANDAMAN AND NICOBAR': { lat: 11.7401, lng: 92.6586, name: 'Andaman & Nicobar' },
  'DADRA AND NAGAR HAVELI': { lat: 20.1809, lng: 73.0169, name: 'Dadra & Nagar Haveli' },
  'DAMAN AND DIU': { lat: 20.4283, lng: 72.8397, name: 'Daman & Diu' },
  'LAKSHADWEEP': { lat: 10.5667, lng: 72.6417, name: 'Lakshadweep' },
};

// Major Indian cities with coordinates
const INDIA_CITY_COORDS: Record<string, { lat: number; lng: number; state: string }> = {
  'MUMBAI': { lat: 19.0760, lng: 72.8777, state: 'Maharashtra' },
  'DELHI': { lat: 28.6139, lng: 77.2090, state: 'Delhi' },
  'BANGALORE': { lat: 12.9716, lng: 77.5946, state: 'Karnataka' },
  'BENGALURU': { lat: 12.9716, lng: 77.5946, state: 'Karnataka' },
  'HYDERABAD': { lat: 17.3850, lng: 78.4867, state: 'Telangana' },
  'CHENNAI': { lat: 13.0827, lng: 80.2707, state: 'Tamil Nadu' },
  'KOLKATA': { lat: 22.5726, lng: 88.3639, state: 'West Bengal' },
  'AHMEDABAD': { lat: 23.0225, lng: 72.5714, state: 'Gujarat' },
  'PUNE': { lat: 18.5204, lng: 73.8567, state: 'Maharashtra' },
  'JAIPUR': { lat: 26.9124, lng: 75.7873, state: 'Rajasthan' },
  'LUCKNOW': { lat: 26.8467, lng: 80.9462, state: 'Uttar Pradesh' },
  'KANPUR': { lat: 26.4499, lng: 80.3319, state: 'Uttar Pradesh' },
  'NAGPUR': { lat: 21.1458, lng: 79.0882, state: 'Maharashtra' },
  'INDORE': { lat: 22.7196, lng: 75.8577, state: 'Madhya Pradesh' },
  'THANE': { lat: 19.2183, lng: 72.9781, state: 'Maharashtra' },
  'BHOPAL': { lat: 23.2599, lng: 77.4126, state: 'Madhya Pradesh' },
  'VISAKHAPATNAM': { lat: 17.6868, lng: 83.2185, state: 'Andhra Pradesh' },
  'PATNA': { lat: 25.5941, lng: 85.1376, state: 'Bihar' },
  'VADODARA': { lat: 22.3072, lng: 73.1812, state: 'Gujarat' },
  'GHAZIABAD': { lat: 28.6692, lng: 77.4538, state: 'Uttar Pradesh' },
  'LUDHIANA': { lat: 30.9010, lng: 75.8573, state: 'Punjab' },
  'AGRA': { lat: 27.1767, lng: 78.0081, state: 'Uttar Pradesh' },
  'NASHIK': { lat: 19.9975, lng: 73.7898, state: 'Maharashtra' },
  'FARIDABAD': { lat: 28.4089, lng: 77.3178, state: 'Haryana' },
  'MEERUT': { lat: 28.9845, lng: 77.7064, state: 'Uttar Pradesh' },
  'RAJKOT': { lat: 22.3039, lng: 70.8022, state: 'Gujarat' },
  'VARANASI': { lat: 25.3176, lng: 82.9739, state: 'Uttar Pradesh' },
  'SRINAGAR': { lat: 34.0837, lng: 74.7973, state: 'Jammu and Kashmir' },
  'AURANGABAD': { lat: 19.8762, lng: 75.3433, state: 'Maharashtra' },
  'DHANBAD': { lat: 23.7957, lng: 86.4304, state: 'Jharkhand' },
  'AMRITSAR': { lat: 31.6340, lng: 74.8723, state: 'Punjab' },
  'NAVI MUMBAI': { lat: 19.0330, lng: 73.0297, state: 'Maharashtra' },
  'ALLAHABAD': { lat: 25.4358, lng: 81.8463, state: 'Uttar Pradesh' },
  'PRAYAGRAJ': { lat: 25.4358, lng: 81.8463, state: 'Uttar Pradesh' },
  'RANCHI': { lat: 23.3441, lng: 85.3096, state: 'Jharkhand' },
  'HOWRAH': { lat: 22.5958, lng: 88.2636, state: 'West Bengal' },
  'COIMBATORE': { lat: 11.0168, lng: 76.9558, state: 'Tamil Nadu' },
  'JABALPUR': { lat: 23.1815, lng: 79.9864, state: 'Madhya Pradesh' },
  'GWALIOR': { lat: 26.2183, lng: 78.1828, state: 'Madhya Pradesh' },
  'VIJAYAWADA': { lat: 16.5062, lng: 80.6480, state: 'Andhra Pradesh' },
  'JODHPUR': { lat: 26.2389, lng: 73.0243, state: 'Rajasthan' },
  'MADURAI': { lat: 9.9252, lng: 78.1198, state: 'Tamil Nadu' },
  'RAIPUR': { lat: 21.2514, lng: 81.6296, state: 'Chhattisgarh' },
  'KOTA': { lat: 25.2138, lng: 75.8648, state: 'Rajasthan' },
  'GUWAHATI': { lat: 26.1445, lng: 91.7362, state: 'Assam' },
  'CHANDIGARH': { lat: 30.7333, lng: 76.7794, state: 'Chandigarh' },
  'SOLAPUR': { lat: 17.6599, lng: 75.9064, state: 'Maharashtra' },
  'HUBLI': { lat: 15.3647, lng: 75.1240, state: 'Karnataka' },
  'TIRUCHIRAPPALLI': { lat: 10.7905, lng: 78.7047, state: 'Tamil Nadu' },
  'BAREILLY': { lat: 28.3670, lng: 79.4304, state: 'Uttar Pradesh' },
  'MYSORE': { lat: 12.2958, lng: 76.6394, state: 'Karnataka' },
  'MYSURU': { lat: 12.2958, lng: 76.6394, state: 'Karnataka' },
  'TIRUPPUR': { lat: 11.1085, lng: 77.3411, state: 'Tamil Nadu' },
  'GURGAON': { lat: 28.4595, lng: 77.0266, state: 'Haryana' },
  'GURUGRAM': { lat: 28.4595, lng: 77.0266, state: 'Haryana' },
  'ALIGARH': { lat: 27.8974, lng: 78.0880, state: 'Uttar Pradesh' },
  'JALANDHAR': { lat: 31.3260, lng: 75.5762, state: 'Punjab' },
  'BHUBANESWAR': { lat: 20.2961, lng: 85.8245, state: 'Odisha' },
  'SALEM': { lat: 11.6643, lng: 78.1460, state: 'Tamil Nadu' },
  'WARANGAL': { lat: 17.9784, lng: 79.5941, state: 'Telangana' },
  'GUNTUR': { lat: 16.3067, lng: 80.4365, state: 'Andhra Pradesh' },
  'BHIWANDI': { lat: 19.2813, lng: 73.0633, state: 'Maharashtra' },
  'SAHARANPUR': { lat: 29.9680, lng: 77.5510, state: 'Uttar Pradesh' },
  'GORAKHPUR': { lat: 26.7606, lng: 83.3732, state: 'Uttar Pradesh' },
  'BIKANER': { lat: 28.0229, lng: 73.3119, state: 'Rajasthan' },
  'AMRAVATI': { lat: 20.9374, lng: 77.7796, state: 'Maharashtra' },
  'NOIDA': { lat: 28.5355, lng: 77.3910, state: 'Uttar Pradesh' },
  'JAMSHEDPUR': { lat: 22.8046, lng: 86.2029, state: 'Jharkhand' },
  'BHILAI': { lat: 21.2094, lng: 81.4285, state: 'Chhattisgarh' },
  'CUTTACK': { lat: 20.4625, lng: 85.8830, state: 'Odisha' },
  'FIROZABAD': { lat: 27.1591, lng: 78.3957, state: 'Uttar Pradesh' },
  'KOCHI': { lat: 9.9312, lng: 76.2673, state: 'Kerala' },
  'COCHIN': { lat: 9.9312, lng: 76.2673, state: 'Kerala' },
  'NELLORE': { lat: 14.4426, lng: 79.9865, state: 'Andhra Pradesh' },
  'BHAVNAGAR': { lat: 21.7645, lng: 72.1519, state: 'Gujarat' },
  'DEHRADUN': { lat: 30.3165, lng: 78.0322, state: 'Uttarakhand' },
  'DURGAPUR': { lat: 23.5204, lng: 87.3119, state: 'West Bengal' },
  'ASANSOL': { lat: 23.6739, lng: 86.9524, state: 'West Bengal' },
  'ROURKELA': { lat: 22.2604, lng: 84.8536, state: 'Odisha' },
  'NANDED': { lat: 19.1383, lng: 77.3210, state: 'Maharashtra' },
  'KOLHAPUR': { lat: 16.7050, lng: 74.2433, state: 'Maharashtra' },
  'AJMER': { lat: 26.4499, lng: 74.6399, state: 'Rajasthan' },
  'GULBARGA': { lat: 17.3297, lng: 76.8343, state: 'Karnataka' },
  'KALABURAGI': { lat: 17.3297, lng: 76.8343, state: 'Karnataka' },
  'JAMNAGAR': { lat: 22.4707, lng: 70.0577, state: 'Gujarat' },
  'UJJAIN': { lat: 23.1765, lng: 75.7885, state: 'Madhya Pradesh' },
  'LONI': { lat: 28.7512, lng: 77.2893, state: 'Uttar Pradesh' },
  'SILIGURI': { lat: 26.7271, lng: 88.6393, state: 'West Bengal' },
  'JHANSI': { lat: 25.4484, lng: 78.5685, state: 'Uttar Pradesh' },
  'ULHASNAGAR': { lat: 19.2215, lng: 73.1645, state: 'Maharashtra' },
  'JAMMU': { lat: 32.7266, lng: 74.8570, state: 'Jammu and Kashmir' },
  'SANGLI': { lat: 16.8524, lng: 74.5815, state: 'Maharashtra' },
  'MANGALORE': { lat: 12.9141, lng: 74.8560, state: 'Karnataka' },
  'MANGALURU': { lat: 12.9141, lng: 74.8560, state: 'Karnataka' },
  'ERODE': { lat: 11.3410, lng: 77.7172, state: 'Tamil Nadu' },
  'BELGAUM': { lat: 15.8497, lng: 74.4977, state: 'Karnataka' },
  'BELAGAVI': { lat: 15.8497, lng: 74.4977, state: 'Karnataka' },
  'AMBATTUR': { lat: 13.1143, lng: 80.1548, state: 'Tamil Nadu' },
  'TIRUNELVELI': { lat: 8.7139, lng: 77.7567, state: 'Tamil Nadu' },
  'MALEGAON': { lat: 20.5579, lng: 74.5089, state: 'Maharashtra' },
  'GAYA': { lat: 24.7955, lng: 85.0002, state: 'Bihar' },
  'UDAIPUR': { lat: 24.5854, lng: 73.7125, state: 'Rajasthan' },
  'MAHESHTALA': { lat: 22.5095, lng: 88.2640, state: 'West Bengal' },
  'DAVANAGERE': { lat: 14.4644, lng: 75.9218, state: 'Karnataka' },
  'KOZHIKODE': { lat: 11.2588, lng: 75.7804, state: 'Kerala' },
  'CALICUT': { lat: 11.2588, lng: 75.7804, state: 'Kerala' },
  'AKOLA': { lat: 20.7002, lng: 77.0082, state: 'Maharashtra' },
  'KURNOOL': { lat: 15.8281, lng: 78.0373, state: 'Andhra Pradesh' },
  'BOKARO': { lat: 23.6693, lng: 86.1511, state: 'Jharkhand' },
  'RAJAHMUNDRY': { lat: 16.9891, lng: 81.7840, state: 'Andhra Pradesh' },
  'BALLARI': { lat: 15.1394, lng: 76.9214, state: 'Karnataka' },
  'BELLARY': { lat: 15.1394, lng: 76.9214, state: 'Karnataka' },
  'AGARTALA': { lat: 23.8315, lng: 91.2868, state: 'Tripura' },
  'BHAGALPUR': { lat: 25.2425, lng: 87.0079, state: 'Bihar' },
  'LATUR': { lat: 18.4088, lng: 76.5604, state: 'Maharashtra' },
  'DHULE': { lat: 20.9042, lng: 74.7749, state: 'Maharashtra' },
  'KORBA': { lat: 22.3595, lng: 82.7501, state: 'Chhattisgarh' },
  'BHILWARA': { lat: 25.3407, lng: 74.6313, state: 'Rajasthan' },
  'BRAHMAPUR': { lat: 19.3150, lng: 84.7941, state: 'Odisha' },
  'MUZAFFARPUR': { lat: 26.1209, lng: 85.3647, state: 'Bihar' },
  'AHMEDNAGAR': { lat: 19.0948, lng: 74.7480, state: 'Maharashtra' },
  'MATHURA': { lat: 27.4924, lng: 77.6737, state: 'Uttar Pradesh' },
  'KOLLAM': { lat: 8.8932, lng: 76.6141, state: 'Kerala' },
  'AVADI': { lat: 13.1067, lng: 80.1009, state: 'Tamil Nadu' },
  'KADAPA': { lat: 14.4674, lng: 78.8241, state: 'Andhra Pradesh' },
  'ANANTAPUR': { lat: 14.6819, lng: 77.6006, state: 'Andhra Pradesh' },
  'KAMARHATI': { lat: 22.6762, lng: 88.3740, state: 'West Bengal' },
  'SAMBALPUR': { lat: 21.4669, lng: 83.9812, state: 'Odisha' },
  'BILASPUR': { lat: 22.0796, lng: 82.1391, state: 'Chhattisgarh' },
  'SHAHJAHANPUR': { lat: 27.8839, lng: 79.9058, state: 'Uttar Pradesh' },
  'SATARA': { lat: 17.6805, lng: 74.0183, state: 'Maharashtra' },
  'BIJAPUR': { lat: 16.8302, lng: 75.7100, state: 'Karnataka' },
  'VIJAYAPURA': { lat: 16.8302, lng: 75.7100, state: 'Karnataka' },
  'RAMPUR': { lat: 28.8019, lng: 79.0250, state: 'Uttar Pradesh' },
  'SHIVAMOGGA': { lat: 13.9299, lng: 75.5681, state: 'Karnataka' },
  'SHIMOGA': { lat: 13.9299, lng: 75.5681, state: 'Karnataka' },
  'CHANDRAPUR': { lat: 19.9615, lng: 79.2961, state: 'Maharashtra' },
  'JUNAGADH': { lat: 21.5222, lng: 70.4579, state: 'Gujarat' },
  'THRISSUR': { lat: 10.5276, lng: 76.2144, state: 'Kerala' },
  'ALWAR': { lat: 27.5530, lng: 76.6346, state: 'Rajasthan' },
  'BARDHAMAN': { lat: 23.2324, lng: 87.8615, state: 'West Bengal' },
  'KULTI': { lat: 23.7281, lng: 86.8533, state: 'West Bengal' },
  'KAKINADA': { lat: 16.9891, lng: 82.2475, state: 'Andhra Pradesh' },
  'NIZAMABAD': { lat: 18.6725, lng: 78.0941, state: 'Telangana' },
  'PARBHANI': { lat: 19.2704, lng: 76.7697, state: 'Maharashtra' },
  'TUMKUR': { lat: 13.3379, lng: 77.1173, state: 'Karnataka' },
  'TUMAKURU': { lat: 13.3379, lng: 77.1173, state: 'Karnataka' },
  'KHAMMAM': { lat: 17.2473, lng: 80.1514, state: 'Telangana' },
  'OZHUKARAI': { lat: 11.9416, lng: 79.7711, state: 'Puducherry' },
  'BIHAR SHARIF': { lat: 25.1982, lng: 85.5239, state: 'Bihar' },
  'PANIPAT': { lat: 29.3909, lng: 76.9635, state: 'Haryana' },
  'DARBHANGA': { lat: 26.1542, lng: 85.8918, state: 'Bihar' },
  'BALLY': { lat: 22.6500, lng: 88.3400, state: 'West Bengal' },
  'AIZAWL': { lat: 23.7271, lng: 92.7176, state: 'Mizoram' },
  'DEWAS': { lat: 22.9623, lng: 76.0508, state: 'Madhya Pradesh' },
  'ICHALKARANJI': { lat: 16.6910, lng: 74.4594, state: 'Maharashtra' },
  'KARNAL': { lat: 29.6857, lng: 76.9905, state: 'Haryana' },
  'BATHINDA': { lat: 30.2110, lng: 74.9455, state: 'Punjab' },
  'JALNA': { lat: 19.8347, lng: 75.8816, state: 'Maharashtra' },
  'ELURU': { lat: 16.7107, lng: 81.0952, state: 'Andhra Pradesh' },
  'BARASAT': { lat: 22.7203, lng: 88.4803, state: 'West Bengal' },
  'KIRARI SULEMAN NAGAR': { lat: 28.7578, lng: 76.9966, state: 'Delhi' },
  'PURNIA': { lat: 25.7771, lng: 87.4753, state: 'Bihar' },
  'SATNA': { lat: 24.5672, lng: 80.8322, state: 'Madhya Pradesh' },
  'MAU': { lat: 25.9419, lng: 83.5611, state: 'Uttar Pradesh' },
  'SONIPAT': { lat: 28.9288, lng: 77.0913, state: 'Haryana' },
  'FARRUKHABAD': { lat: 27.3906, lng: 79.5820, state: 'Uttar Pradesh' },
  'SAGAR': { lat: 23.8388, lng: 78.7378, state: 'Madhya Pradesh' },
  'DURG': { lat: 21.1904, lng: 81.2849, state: 'Chhattisgarh' },
  'IMPHAL': { lat: 24.8170, lng: 93.9368, state: 'Manipur' },
  'RATLAM': { lat: 23.3341, lng: 75.0367, state: 'Madhya Pradesh' },
  'HAPUR': { lat: 28.7437, lng: 77.7628, state: 'Uttar Pradesh' },
  'ARRAH': { lat: 25.5549, lng: 84.6602, state: 'Bihar' },
  'KARIMNAGAR': { lat: 18.4386, lng: 79.1288, state: 'Telangana' },
  'ANANTAPURAM': { lat: 14.6819, lng: 77.6006, state: 'Andhra Pradesh' },
  'ETAWAH': { lat: 26.7856, lng: 79.0158, state: 'Uttar Pradesh' },
  'AMBERNATH': { lat: 19.1863, lng: 73.1918, state: 'Maharashtra' },
  'NORTH DUMDUM': { lat: 22.6574, lng: 88.4029, state: 'West Bengal' },
  'BHARATPUR': { lat: 27.2152, lng: 77.5030, state: 'Rajasthan' },
  'BEGUSARAI': { lat: 25.4182, lng: 86.1272, state: 'Bihar' },
  'NEW DELHI': { lat: 28.6139, lng: 77.2090, state: 'Delhi' },
  'GANDHIDHAM': { lat: 23.0753, lng: 70.1337, state: 'Gujarat' },
  'BARANAGAR': { lat: 22.6435, lng: 88.3767, state: 'West Bengal' },
  'TIRUVOTTIYUR': { lat: 13.1600, lng: 80.3000, state: 'Tamil Nadu' },
  'PONDICHERRY': { lat: 11.9416, lng: 79.8083, state: 'Puducherry' },
  'SIKAR': { lat: 27.6094, lng: 75.1398, state: 'Rajasthan' },
  'THOOTHUKUDI': { lat: 8.7642, lng: 78.1348, state: 'Tamil Nadu' },
  'TUTICORIN': { lat: 8.7642, lng: 78.1348, state: 'Tamil Nadu' },
  'REWA': { lat: 24.5362, lng: 81.2985, state: 'Madhya Pradesh' },
  'MIRZAPUR': { lat: 25.1460, lng: 82.5690, state: 'Uttar Pradesh' },
  'RAICHUR': { lat: 16.2120, lng: 77.3439, state: 'Karnataka' },
  'PALI': { lat: 25.7711, lng: 73.3234, state: 'Rajasthan' },
  'RAMAGUNDAM': { lat: 18.8048, lng: 79.4740, state: 'Telangana' },
  'SILCHAR': { lat: 24.8333, lng: 92.7789, state: 'Assam' },
  'HARIDWAR': { lat: 29.9457, lng: 78.1642, state: 'Uttarakhand' },
  'VIJAYANAGARAM': { lat: 18.1066, lng: 83.3956, state: 'Andhra Pradesh' },
  'TENALI': { lat: 16.2428, lng: 80.6400, state: 'Andhra Pradesh' },
  'NAGERCOIL': { lat: 8.1833, lng: 77.4119, state: 'Tamil Nadu' },
  'SRI GANGANAGAR': { lat: 29.9038, lng: 73.8772, state: 'Rajasthan' },
  'KARAWAL NAGAR': { lat: 28.7695, lng: 77.2930, state: 'Delhi' },
  'MANGO': { lat: 22.8260, lng: 86.2167, state: 'Jharkhand' },
  'THANJAVUR': { lat: 10.7870, lng: 79.1378, state: 'Tamil Nadu' },
  'BULANDSHAHR': { lat: 28.4070, lng: 77.8498, state: 'Uttar Pradesh' },
  'ULUBERIA': { lat: 22.4700, lng: 88.1100, state: 'West Bengal' },
  'MURWARA': { lat: 23.8388, lng: 80.3916, state: 'Madhya Pradesh' },
  'KATNI': { lat: 23.8388, lng: 80.3916, state: 'Madhya Pradesh' },
  'SAMBHAL': { lat: 28.5904, lng: 78.5718, state: 'Uttar Pradesh' },
  'SINGRAULI': { lat: 24.1990, lng: 82.6758, state: 'Madhya Pradesh' },
  'NADIAD': { lat: 22.6916, lng: 72.8634, state: 'Gujarat' },
  'SECUNDERABAD': { lat: 17.4399, lng: 78.4983, state: 'Telangana' },
  'NAIHATI': { lat: 22.8917, lng: 88.4217, state: 'West Bengal' },
  'YAMUNANAGAR': { lat: 30.1290, lng: 77.2674, state: 'Haryana' },
  'BIDHANNAGAR': { lat: 22.5958, lng: 88.4225, state: 'West Bengal' },
  'PALLAVARAM': { lat: 12.9675, lng: 80.1491, state: 'Tamil Nadu' },
  'BIDAR': { lat: 17.9133, lng: 77.5197, state: 'Karnataka' },
  'MUNGER': { lat: 25.3708, lng: 86.4716, state: 'Bihar' },
  'PANCHKULA': { lat: 30.6942, lng: 76.8606, state: 'Haryana' },
  'BURHANPUR': { lat: 21.3104, lng: 76.2301, state: 'Madhya Pradesh' },
  'RAURKELA INDUSTRIAL TOWNSHIP': { lat: 22.2604, lng: 84.8536, state: 'Odisha' },
  'KHARAGPUR': { lat: 22.3460, lng: 87.2320, state: 'West Bengal' },
  'DINDIGUL': { lat: 10.3624, lng: 77.9695, state: 'Tamil Nadu' },
  'GANDHINAGAR': { lat: 23.2156, lng: 72.6369, state: 'Gujarat' },
  'HOSPET': { lat: 15.2689, lng: 76.3909, state: 'Karnataka' },
  'HOSAPETE': { lat: 15.2689, lng: 76.3909, state: 'Karnataka' },
  'NANGLOI JAT': { lat: 28.6833, lng: 77.0667, state: 'Delhi' },
  'MALDA': { lat: 25.0108, lng: 88.1411, state: 'West Bengal' },
  'ENGLISH BAZAR': { lat: 25.0108, lng: 88.1411, state: 'West Bengal' },
  'ONGOLE': { lat: 15.5057, lng: 80.0499, state: 'Andhra Pradesh' },
  'DEOGHAR': { lat: 24.4855, lng: 86.6962, state: 'Jharkhand' },
  'CHAPRA': { lat: 25.7848, lng: 84.7463, state: 'Bihar' },
  'HALDIA': { lat: 22.0667, lng: 88.0698, state: 'West Bengal' },
  'KHANDWA': { lat: 21.8264, lng: 76.3528, state: 'Madhya Pradesh' },
  'MORENA': { lat: 26.5000, lng: 78.0000, state: 'Madhya Pradesh' },
  'AMROHA': { lat: 28.9044, lng: 78.4673, state: 'Uttar Pradesh' },
  'BHIND': { lat: 26.5645, lng: 78.7871, state: 'Madhya Pradesh' },
  'PORBANDAR': { lat: 21.6417, lng: 69.6293, state: 'Gujarat' },
  'BHUSAWAL': { lat: 21.0486, lng: 75.7828, state: 'Maharashtra' },
  'ORAI': { lat: 25.9917, lng: 79.4517, state: 'Uttar Pradesh' },
  'BAHRAICH': { lat: 27.5706, lng: 81.5938, state: 'Uttar Pradesh' },
  'VELLORE': { lat: 12.9165, lng: 79.1325, state: 'Tamil Nadu' },
  'MEHSANA': { lat: 23.5880, lng: 72.3693, state: 'Gujarat' },
  'RAIGANJ': { lat: 25.6217, lng: 88.1247, state: 'West Bengal' },
  'SIRSA': { lat: 29.5350, lng: 75.0283, state: 'Haryana' },
  'DANAPUR': { lat: 25.6000, lng: 85.0500, state: 'Bihar' },
  'SERAMPORE': { lat: 22.7500, lng: 88.3400, state: 'West Bengal' },
  'SULTAN PUR MAJRA': { lat: 28.6970, lng: 77.0842, state: 'Delhi' },
  'GUNA': { lat: 24.6481, lng: 77.3148, state: 'Madhya Pradesh' },
  'JAUNPUR': { lat: 25.7464, lng: 82.6837, state: 'Uttar Pradesh' },
  'PANVEL': { lat: 18.9894, lng: 73.1175, state: 'Maharashtra' },
  'SHIVPURI': { lat: 25.4258, lng: 77.6631, state: 'Madhya Pradesh' },
  'SURENDRANAGAR DUDHREJ': { lat: 22.7364, lng: 71.6258, state: 'Gujarat' },
  'UNNAO': { lat: 26.5393, lng: 80.4878, state: 'Uttar Pradesh' },
  'HUGLI CHINSURAH': { lat: 22.9000, lng: 88.3833, state: 'West Bengal' },
  'ALAPPUZHA': { lat: 9.4981, lng: 76.3388, state: 'Kerala' },
  'ALLEPPEY': { lat: 9.4981, lng: 76.3388, state: 'Kerala' },
  'KOTTAYAM': { lat: 9.5916, lng: 76.5222, state: 'Kerala' },
  'MACHILIPATNAM': { lat: 16.1875, lng: 81.1389, state: 'Andhra Pradesh' },
  'SHIMLA': { lat: 31.1048, lng: 77.1734, state: 'Himachal Pradesh' },
  'ADONI': { lat: 15.6279, lng: 77.2750, state: 'Andhra Pradesh' },
  'UDUPI': { lat: 13.3389, lng: 74.7451, state: 'Karnataka' },
  'KATIHAR': { lat: 25.5392, lng: 87.5719, state: 'Bihar' },
  'PRODDATUR': { lat: 14.7502, lng: 78.5481, state: 'Andhra Pradesh' },
  'MAHBUBNAGAR': { lat: 16.7488, lng: 77.9855, state: 'Telangana' },
  'SAHARSA': { lat: 25.8803, lng: 86.5979, state: 'Bihar' },
  'DIBRUGARH': { lat: 27.4728, lng: 94.9120, state: 'Assam' },
  'GANGTOK': { lat: 27.3389, lng: 88.6065, state: 'Sikkim' },
  'KOHIMA': { lat: 25.6751, lng: 94.1086, state: 'Nagaland' },
  'ITANAGAR': { lat: 27.0844, lng: 93.6053, state: 'Arunachal Pradesh' },
  'SHILLONG': { lat: 25.5788, lng: 91.8933, state: 'Meghalaya' },
  'PORT BLAIR': { lat: 11.6234, lng: 92.7265, state: 'Andaman and Nicobar' },
  'KAVARATTI': { lat: 10.5593, lng: 72.6358, state: 'Lakshadweep' },
  'SILVASSA': { lat: 20.2766, lng: 73.0166, state: 'Dadra and Nagar Haveli' },
  'DAMAN': { lat: 20.3974, lng: 72.8328, state: 'Daman and Diu' },
  'DIU': { lat: 20.7141, lng: 70.9875, state: 'Daman and Diu' },
};

// Format Indian currency
const formatIndianCurrency = (num: number): string => {
  if (num >= 10000000) {
    return `₹${(num / 10000000).toFixed(2)} Cr`;
  } else if (num >= 100000) {
    return `₹${(num / 100000).toFixed(2)} L`;
  } else if (num >= 1000) {
    return `₹${(num / 1000).toFixed(2)} K`;
  }
  return `₹${num.toFixed(2)}`;
};

interface StateData {
  name: string;
  value: number;
  quantity?: number;
}

interface CityData {
  name: string;
  value: number;
  state?: string;
}

interface IndiaMapProps {
  stateData: StateData[];
  cityData: CityData[];
  title?: string;
  viewMode?: 'state' | 'city';
  loading?: boolean;
}

// Convert lat/lng to SVG coordinates
const latLngToSvg = (lat: number, lng: number, width: number, height: number) => {
  // India bounds approximately: lat 8-37, lng 68-98
  const minLat = 6;
  const maxLat = 38;
  const minLng = 66;
  const maxLng = 100;
  
  const x = ((lng - minLng) / (maxLng - minLng)) * width;
  const y = height - ((lat - minLat) / (maxLat - minLat)) * height;
  
  return { x, y };
};

export const IndiaMap: React.FC<IndiaMapProps> = ({
  stateData,
  cityData,
  title = '🗺️ Geographic Revenue Distribution',
  viewMode = 'state',
  loading = false,
}) => {
  const [hoveredItem, setHoveredItem] = useState<{ name: string; value: number; x: number; y: number } | null>(null);
  const [currentViewMode, setCurrentViewMode] = useState<'state' | 'city'>(viewMode);
  
  const width = 500;
  const height = 550;
  
  // Calculate max values for scaling
  const maxStateValue = useMemo(() => {
    return Math.max(...stateData.map(s => s.value), 1);
  }, [stateData]);
  
  const maxCityValue = useMemo(() => {
    return Math.max(...cityData.map(c => c.value), 1);
  }, [cityData]);
  
  // Generate state pins
  const statePins = useMemo(() => {
    return stateData.map(state => {
      const normalizedName = state.name.toUpperCase().trim();
      const coords = INDIA_STATE_COORDS[normalizedName];
      
      if (!coords) return null;
      
      const { x, y } = latLngToSvg(coords.lat, coords.lng, width, height);
      const size = 8 + (state.value / maxStateValue) * 20;
      
      return {
        ...state,
        x,
        y,
        size,
        displayName: coords.name,
      };
    }).filter(Boolean);
  }, [stateData, maxStateValue]);
  
  // Generate city pins
  const cityPins = useMemo(() => {
    return cityData.map(city => {
      const normalizedName = city.name.toUpperCase().trim();
      const coords = INDIA_CITY_COORDS[normalizedName];
      
      if (!coords) return null;
      
      const { x, y } = latLngToSvg(coords.lat, coords.lng, width, height);
      const size = 5 + (city.value / maxCityValue) * 15;
      
      return {
        ...city,
        x,
        y,
        size,
        stateName: coords.state,
      };
    }).filter(Boolean);
  }, [cityData, maxCityValue]);
  
  if (loading) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setCurrentViewMode('state')}
            className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              currentViewMode === 'state'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            States
          </button>
          <button
            onClick={() => setCurrentViewMode('city')}
            className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
              currentViewMode === 'city'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Cities
          </button>
        </div>
      </div>
      
      <div className="relative">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto"
          style={{ maxHeight: '500px' }}
        >
          {/* Background map outline of India - simplified path */}
          <path
            d="M 140 80 
               Q 180 40, 220 50
               Q 260 30, 300 60
               Q 340 40, 380 70
               Q 400 100, 410 140
               Q 430 180, 420 220
               Q 440 260, 430 300
               Q 450 340, 440 380
               Q 460 420, 420 460
               Q 380 500, 340 490
               Q 300 510, 260 480
               Q 220 500, 180 470
               Q 140 490, 120 450
               Q 90 420, 100 380
               Q 80 340, 90 300
               Q 70 260, 80 220
               Q 60 180, 80 140
               Q 70 100, 100 80
               Q 120 60, 140 80
               Z"
            fill="#E5E7EB"
            stroke="#9CA3AF"
            strokeWidth="2"
          />
          
          {/* State pins */}
          {currentViewMode === 'state' && statePins.map((pin: any, idx) => (
            <g key={`state-${idx}`}>
              <circle
                cx={pin.x}
                cy={pin.y}
                r={pin.size}
                fill="rgba(79, 70, 229, 0.6)"
                stroke="#4F46E5"
                strokeWidth="2"
                className="cursor-pointer transition-all duration-200 hover:fill-opacity-80"
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setHoveredItem({
                    name: pin.displayName || pin.name,
                    value: pin.value,
                    x: pin.x,
                    y: pin.y,
                  });
                }}
                onMouseLeave={() => setHoveredItem(null)}
              />
              {pin.size > 15 && (
                <text
                  x={pin.x}
                  y={pin.y + pin.size + 12}
                  textAnchor="middle"
                  fontSize="9"
                  fill="#374151"
                  fontWeight="500"
                >
                  {pin.displayName?.substring(0, 10) || pin.name?.substring(0, 10)}
                </text>
              )}
            </g>
          ))}
          
          {/* City pins */}
          {currentViewMode === 'city' && cityPins.map((pin: any, idx) => (
            <g key={`city-${idx}`}>
              <circle
                cx={pin.x}
                cy={pin.y}
                r={pin.size}
                fill="rgba(16, 185, 129, 0.6)"
                stroke="#10B981"
                strokeWidth="1.5"
                className="cursor-pointer transition-all duration-200 hover:fill-opacity-80"
                onMouseEnter={() => {
                  setHoveredItem({
                    name: pin.name,
                    value: pin.value,
                    x: pin.x,
                    y: pin.y,
                  });
                }}
                onMouseLeave={() => setHoveredItem(null)}
              />
              {pin.size > 10 && (
                <text
                  x={pin.x}
                  y={pin.y + pin.size + 10}
                  textAnchor="middle"
                  fontSize="8"
                  fill="#374151"
                  fontWeight="500"
                >
                  {pin.name?.substring(0, 8)}
                </text>
              )}
            </g>
          ))}
        </svg>
        
        {/* Tooltip */}
        {hoveredItem && (
          <div
            className="absolute bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm pointer-events-none z-10"
            style={{
              left: `${(hoveredItem.x / width) * 100}%`,
              top: `${(hoveredItem.y / height) * 100}%`,
              transform: 'translate(-50%, -120%)',
            }}
          >
            <div className="font-semibold">{hoveredItem.name}</div>
            <div className="text-green-400">{formatIndianCurrency(hoveredItem.value)}</div>
          </div>
        )}
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <div className={`w-3 h-3 rounded-full ${currentViewMode === 'state' ? 'bg-indigo-500' : 'bg-emerald-500'}`}></div>
            <span>{currentViewMode === 'state' ? 'State Revenue' : 'City Revenue'}</span>
          </div>
          <div className="text-gray-400">|</div>
          <span>Circle size = Revenue amount</span>
        </div>
        <div>
          <span className="font-medium">
            {currentViewMode === 'state' ? statePins.length : cityPins.length} locations
          </span>
        </div>
      </div>
      
      {/* Top locations list */}
      <div className="mt-4 border-t border-gray-100 pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">
          Top {currentViewMode === 'state' ? 'States' : 'Cities'} by Revenue
        </h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {(currentViewMode === 'state' ? stateData : cityData).slice(0, 6).map((item, idx) => (
            <div key={idx} className="flex justify-between items-center bg-gray-50 px-2 py-1.5 rounded">
              <span className="text-gray-700 truncate">{idx + 1}. {item.name}</span>
              <span className="text-green-600 font-medium ml-2">{formatIndianCurrency(item.value)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default IndiaMap;
