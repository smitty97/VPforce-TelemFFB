#include <stdio.h>
#include <string.h>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cstdarg>
#include <string>
#include <vector>
#include <map>
#include <cstring>
#include <winsock2.h>
#include <thread>
#define XPLM300 1
#include "XPLMProcessing.h"
#include "XPLMDataAccess.h"
#include "XPLMUtilities.h"
#include "XPLMPlugin.h"
#include "XPLMPlanes.h"



/* UDP socket variables */
SOCKET udpSocket_tx;
struct sockaddr_in serverAddr_tx;
SOCKET udpSocket_rx;
struct sockaddr_in serverAddr_rx;
bool gTerminateReceiveThread = false;

/* Data refs we will record. */
static XPLMDataRef gPaused = XPLMFindDataRef("sim/time/paused");                                        // boolean � int � v6.60+
static XPLMDataRef gOnGround = XPLMFindDataRef("sim/flightmodel/failures/onground_all");                // int � v6.60+
static XPLMDataRef gRetractable = XPLMFindDataRef("sim/aircraft/gear/acf_gear_retract");                // boolean � int � v6.60+
static XPLMDataRef gFlaps = XPLMFindDataRef("sim/cockpit2/controls/flap_system_deploy_ratio");          // [0..1] � float � v6.60
static XPLMDataRef gGear = XPLMFindDataRef("sim/flightmodel2/gear/deploy_ratio");                       // ratio � float[gear] � v9.00 +
static XPLMDataRef gGs_axil = XPLMFindDataRef("sim/flightmodel/forces/g_axil");                         // Gs � float � v6.60+
static XPLMDataRef gGs_nrml = XPLMFindDataRef("sim/flightmodel/forces/g_nrml");                         // Gs � float � v6.60+
static XPLMDataRef gGs_side = XPLMFindDataRef("sim/flightmodel/forces/g_side");                         // Gs � float � v6.60+
static XPLMDataRef gAccLocal_x = XPLMFindDataRef("sim/flightmodel/position/local_ax");                  // mtr/sec2 � float � v6.60+
static XPLMDataRef gAccLocal_y = XPLMFindDataRef("sim/flightmodel/position/local_ay");                  // mtr/sec2 � float � v6.60+
static XPLMDataRef gAccLocal_z = XPLMFindDataRef("sim/flightmodel/position/local_az");                  // mtr/sec2 � float � v6.60+
static XPLMDataRef gVelAcf_x = XPLMFindDataRef("sim/flightmodel/forces/vx_acf_axis");                   // m/s � float � v6.60+
static XPLMDataRef gVelAcf_y = XPLMFindDataRef("sim/flightmodel/forces/vy_acf_axis");                   // m/s � float � v6.60+
static XPLMDataRef gVelAcf_z = XPLMFindDataRef("sim/flightmodel/forces/vz_acf_axis");                   // m/s � float � v6.60+
static XPLMDataRef gTAS = XPLMFindDataRef("sim/flightmodel/position/true_airspeed");                    // m/s � float � v6.60+
static XPLMDataRef gAirDensity = XPLMFindDataRef("sim/weather/rho");                                    // kg/cu m float � v6.60+
static XPLMDataRef gDynPress = XPLMFindDataRef("sim/flightmodel/misc/Qstatic");                         // psf � float � v6.60+
static XPLMDataRef gPropThrust = XPLMFindDataRef("sim/flightmodel/engine/POINT_thrust");                // newtons � float[16] � v6.60+
static XPLMDataRef gAoA = XPLMFindDataRef("sim/flightmodel/position/alpha");                            // degrees � float � v6.60+
static XPLMDataRef gWarnAlpha = XPLMFindDataRef("sim/aircraft/overflow/acf_stall_warn_alpha");          // degrees � float � v6.60+
static XPLMDataRef gSlip = XPLMFindDataRef("sim/flightmodel/position/beta");                            // degrees � float � v6.60+
static XPLMDataRef gWoW = XPLMFindDataRef("sim/flightmodel2/gear/tire_vertical_deflection_mtr");        // meters � float[gear] � v9.00+
static XPLMDataRef gEngRPM = XPLMFindDataRef("sim/flightmodel/engine/ENGN_tacrad");                     // rad/sec � float[16] � v6.60+
static XPLMDataRef gEngPCT = XPLMFindDataRef("sim/flightmodel/engine/ENGN_N1_");                        // percent � float[16] � v6.60+
static XPLMDataRef gPropRPM = XPLMFindDataRef("sim/flightmodel/engine/POINT_tacrad");                   // rad/sec � float[16] � v6.60+
static XPLMDataRef gRudDefl_l = XPLMFindDataRef("sim/flightmodel/controls/ldruddef");                   // degrees � float � v6.60+
static XPLMDataRef gRudDefl_r = XPLMFindDataRef("sim/flightmodel/controls/rdruddef");                   // degrees � float � v6.60+
static XPLMDataRef gVne = XPLMFindDataRef("sim/aircraft/view/acf_Vne");                                 // kias � float � v6.60+
static XPLMDataRef gVso = XPLMFindDataRef("sim/aircraft/view/acf_Vso");                                 // kias � float � v6.60+
static XPLMDataRef gVfe = XPLMFindDataRef("sim/aircraft/view/acf_Vfe");                                 // kias � float � v6.60+
static XPLMDataRef gVle = XPLMFindDataRef("sim/aircraft/overflow/acf_Vle");                             // kias  float � v6.60 +


static XPLMDataRef gCollectiveOvd = XPLMFindDataRef("sim/operation/override/override_prop_pitch");
static XPLMDataRef gRollOvd = XPLMFindDataRef("sim/operation/override/override_joystick_roll");
static XPLMDataRef gPitchOvd = XPLMFindDataRef("sim/operation/override/override_joystick_pitch");
static XPLMDataRef gYawOvd = XPLMFindDataRef("sim/operation/override/override_joystick_heading");

static XPLMDataRef gRollCenter = XPLMFindDataRef("sim/joystick/joystick_roll_center");

static XPLMDataRef gCollectiveRatio = XPLMFindDataRef("sim/cockpit2/engine/actuators/prop_ratio_all");
static XPLMDataRef gRollRatio = XPLMFindDataRef("sim/joystick/yoke_roll_ratio");
static XPLMDataRef gPitchRatio = XPLMFindDataRef("sim/joystick/yoke_pitch_ratio");
static XPLMDataRef gYawRatio = XPLMFindDataRef("sim/joystick/yoke_heading_ratio");


std::map<std::string, std::string> telemetryData;

static float MyFlightLoopCallback(float inElapsedSinceLastCall, float inElapsedTimeSinceLastFlightLoop, int inCounter, void* inRefcon);

const float kt_2_mps = 0.51444; // convert knots to meters per second
const float radps_2_rpm = 9.5493; // convert rad/sec to rev/min
const float fps_2_g = 0.031081; // convert feet per second to g

std::string FloatToString(float value, int precision, float conversionFactor = 1.0) {
    value *= conversionFactor; // Apply the conversion factor
    std::ostringstream stream;
    stream << std::fixed << std::setprecision(precision) << value;
    return stream.str();
}

// Function to convert an array of floats to a formatted string with an optional conversion factor
std::string FloatArrayToString(XPLMDataRef dataRef, int offset, int size, float conversionFactor = 1.0) {
    // Use std::vector for dynamic memory allocation
    std::vector<float> dataArray(size);

    // Retrieve the entire array of values
    XPLMGetDatavf(dataRef, dataArray.data(), offset, size);

    std::ostringstream formattedString;

    // Set precision for floating-point values
    formattedString << std::fixed << std::setprecision(3);

    for (int i = 0; i < size; ++i) {
        formattedString << dataArray[i] * conversionFactor; // Apply the conversion factor
        if (i < size - 1) {
            formattedString << "~";  // Add tilde separator between values, except for the last one
        }
    }

    return formattedString.str();
}

void CollectTelemetryData()
{
    // Get the aircraft name
    char aircraftName[256];
    char aircraftPath[256];
    XPLMGetNthAircraftModel(0, aircraftName, aircraftPath);

    // Strip the file extension from the aircraft name
    char* lastDot = strrchr(aircraftName, '.');
    if (lastDot != nullptr) {
        *lastDot = '\0';
    }

    telemetryData["src"] = "XPLANE";
    telemetryData["N"] = aircraftName;
    telemetryData["STOP"] = std::to_string(XPLMGetDatai(gPaused));
    telemetryData["SimPaused"] = std::to_string(XPLMGetDatai(gPaused));
    telemetryData["SimOnGround"] = std::to_string(XPLMGetDatai(gOnGround));
    telemetryData["RetractableGear"] = std::to_string(XPLMGetDatai(gRetractable));
    telemetryData["T"] = FloatToString(XPLMGetElapsedTime(), 3);
    telemetryData["G"] = FloatToString(XPLMGetDataf(gGs_nrml), 3);
    telemetryData["Gaxil"] = FloatToString(XPLMGetDataf(gGs_axil), 3);
    telemetryData["Gside"] = FloatToString(XPLMGetDataf(gGs_side), 3);

    telemetryData["TAS"] = FloatToString(XPLMGetDataf(gTAS), 3);
    telemetryData["AirDensity"] = FloatToString(XPLMGetDataf(gAirDensity), 3);
    telemetryData["DynPressure"] = FloatToString(XPLMGetDataf(gDynPress), 3);
    telemetryData["AoA"] = FloatToString(XPLMGetDataf(gAoA), 3);
    telemetryData["WarnAlpha"] = FloatToString(XPLMGetDataf(gWarnAlpha), 3);
    telemetryData["SideSlip"] = FloatToString(XPLMGetDataf(gSlip), 3);
    telemetryData["Vne"] = FloatToString(XPLMGetDataf(gVne) * kt_2_mps, 3);
    telemetryData["Vso"] = FloatToString(XPLMGetDataf(gVso) * kt_2_mps, 3);
    telemetryData["Vfe"] = FloatToString(XPLMGetDataf(gVfe) * kt_2_mps, 3);
    telemetryData["Vle"] = FloatToString(XPLMGetDataf(gVle) * kt_2_mps, 3);

    telemetryData["WeightOnWheels"] = FloatArrayToString(gWoW, 0, 4);
    telemetryData["EngRPM"] = FloatArrayToString(gEngRPM, 0, 4, radps_2_rpm);
    telemetryData["EngPCT"] = FloatArrayToString(gEngPCT, 0, 4);
    telemetryData["PropRPM"] = FloatArrayToString(gPropRPM, 0, 4, radps_2_rpm);
    telemetryData["PropThrust"] = FloatArrayToString(gPropThrust, 0, 4);
    telemetryData["RudderDefl"] = FloatToString(XPLMGetDataf(gRudDefl_l), 3);
    telemetryData["RudderDefl_l"] = FloatToString(XPLMGetDataf(gRudDefl_l), 3);
    telemetryData["RudderDefl_r"] = FloatToString(XPLMGetDataf(gRudDefl_r), 3);

    telemetryData["AccBody"] =  FloatToString(XPLMGetDataf(gAccLocal_x) * fps_2_g, 3) + "~" + FloatToString(XPLMGetDataf(gAccLocal_y) * fps_2_g, 3) + "~" + FloatToString(XPLMGetDataf(gAccLocal_z) * fps_2_g, 3);
    telemetryData["VelAcf"] =  FloatToString(XPLMGetDataf(gVelAcf_x), 3) + "~" + FloatToString(XPLMGetDataf(gVelAcf_y), 3) + "~" + FloatToString(-XPLMGetDataf(gVelAcf_z), 3);
    telemetryData["Flaps"] = FloatToString(XPLMGetDataf(gFlaps), 3);
    telemetryData["Gear"] = FloatArrayToString(gGear,0, 3);


}



void FormatAndSendTelemetryData()
{
    // Create a string with the data for UDP transmission
    std::string dataString;

    for (const auto& entry : telemetryData) {
        dataString += entry.first + "=" + entry.second + ";";
    }

    // Send the data over the UDP socket
    sendto(udpSocket_tx, dataString.c_str(), dataString.length(), 0, (struct sockaddr*)&serverAddr_tx, sizeof(serverAddr_tx));
}

void ReceiveAndProcessMessages() {
    char buffer[1024];
    int recvlen;
    struct sockaddr_in senderAddr;
    int senderAddrSize = sizeof(senderAddr);

    recvlen = recvfrom(udpSocket_rx, buffer, sizeof(buffer), 0, (struct sockaddr*)&senderAddr, &senderAddrSize);
    if (recvlen > 0) {
        // Process the received message (you can parse and handle the message here)
        buffer[recvlen] = 0; // Null-terminate the received data
        // Call your message processing function here with 'buffer'
    }
}

void ReceiveThread() {
    while (!gTerminateReceiveThread) {
        ReceiveAndProcessMessages();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}

PLUGIN_API int XPluginStart(char* outName, char* outSig, char* outDesc)
{

    strcpy(outName, "TelemFFB-XPP");
    strcpy(outSig, "vpforce.telemffb.xpplugin");
    strcpy(outDesc, "Collect and send Telemetry for FFB processing");


    /* Find the data refs we want to record. */



    // Initialize Winsock
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
    {
        XPLMDebugString("Failed to initialize Winsock\n");
        return 0;
    }

    // Create a UDP socket
    udpSocket_tx = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);

    if (udpSocket_tx == INVALID_SOCKET)
    {
        XPLMDebugString("Failed to create UDP socket\n");
        WSACleanup();
        return 0;
    }

    // Set up server address information
    memset(&serverAddr_tx, 0, sizeof(serverAddr_tx));
    serverAddr_tx.sin_family = AF_INET;
    serverAddr_tx.sin_port = htons(34390); // Set the desired port number
    serverAddr_tx.sin_addr.s_addr = inet_addr("127.255.255.255"); // Send to localhost (127.0.0.1)


    udpSocket_rx = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);

    if (udpSocket_rx == INVALID_SOCKET)
    {
        XPLMDebugString("Failed to create receive UDP socket\n");
        WSACleanup();
        return 0;
    }

    // Set up server address information for the receive socket
    memset(&serverAddr_rx, 0, sizeof(serverAddr_rx));
    serverAddr_rx.sin_family = AF_INET;
    serverAddr_rx.sin_port = htons(34391);  // Set the desired port number for receiving
    serverAddr_rx.sin_addr.s_addr = inet_addr("127.0.0.1");
    bind(udpSocket_rx, (struct sockaddr*)&serverAddr_rx, sizeof(serverAddr_rx));


    /* Register our callback for once a second.  Positive intervals
     * are in seconds, negative are the negative of sim frames.  Zero
     * registers but does not schedule a callback for time. */
    XPLMRegisterFlightLoopCallback(
        MyFlightLoopCallback, /* Callback */
        -1,                  /* Interval */
        NULL);                /* refcon not used. */

    std::thread receiveThread(ReceiveThread);
    receiveThread.detach();  // Detach the thread to allow it to run independently


    return 1;
}

PLUGIN_API void XPluginStop(void)
{
    /* Unregister the callback */
    XPLMUnregisterFlightLoopCallback(MyFlightLoopCallback, NULL);

    gTerminateReceiveThread = true;

    // Close the UDP socket
    closesocket(udpSocket_tx);
    closesocket(udpSocket_rx);
    WSACleanup();
}

PLUGIN_API void XPluginDisable(void)
{
    /* do any clean up here */
}

PLUGIN_API int XPluginEnable(void)
{
    return 1;
}

PLUGIN_API void XPluginReceiveMessage(XPLMPluginID inFromWho, int inMessage, void* inParam)
{

}

float MyFlightLoopCallback(float inElapsedSinceLastCall, float inElapsedTimeSinceLastFlightLoop, int inCounter, void* inRefcon)
{

    // Collect telemetry data
    CollectTelemetryData();

    // Format and send telemetry data
    FormatAndSendTelemetryData();

 

    // Return -1 to indicate we want to be called on next opportunity
    return -1;
}
