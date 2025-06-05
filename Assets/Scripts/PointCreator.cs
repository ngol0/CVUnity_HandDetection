using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PointCreator : MonoBehaviour
{
    [SerializeField] GameObject pointPrefab;
    [SerializeField] GameObject linePrefab;
    [SerializeField] HandTracking tracking;
    [SerializeField] int numberOfPoints = 21;
    [SerializeField] int numberOfLine = 21;
    [SerializeField] Transform pointRoot;
    [SerializeField] Transform lineRoot;
    
    private int[,] handConnections = new int[,]
    {
        // WRIST TO PALM BASE
        {0, 1},   // Wrist to Thumb CMC
        {0, 5},   // Wrist to Index MCP
        {0, 17},  // Wrist to Pinky MCP
        
        // PALM CONNECTIONS (connecting the base of fingers)
        {5, 9},   // Index MCP to Middle MCP
        {9, 13},  // Middle MCP to Ring MCP
        {13, 17}, // Ring MCP to Pinky MCP
        
        // THUMB CHAIN
        {1, 2},   // Thumb CMC to MCP
        {2, 3},   // Thumb MCP to IP
        {3, 4},   // Thumb IP to TIP
        
        // INDEX FINGER CHAIN
        {5, 6},   // Index MCP to PIP
        {6, 7},   // Index PIP to DIP
        {7, 8},   // Index DIP to TIP
        
        // MIDDLE FINGER CHAIN
        {9, 10},  // Middle MCP to PIP
        {10, 11}, // Middle PIP to DIP
        {11, 12}, // Middle DIP to TIP
        
        // RING FINGER CHAIN
        {13, 14}, // Ring MCP to PIP
        {14, 15}, // Ring PIP to DIP
        {15, 16}, // Ring DIP to TIP
        
        // PINKY CHAIN
        {17, 18}, // Pinky MCP to PIP
        {18, 19}, // Pinky PIP to DIP
        {19, 20}  // Pinky DIP to TIP
    };

    void Start()
    {
        // Create a point at the origin
        for (int i = 0; i < numberOfPoints; i++)
        {
            Vector3 position = new Vector3(0, 0, 0);
            var point = Instantiate(pointPrefab, position, Quaternion.identity, pointRoot);
            tracking.handPoints.Add(point);
        }

        // Create a point at the origin
        for (int i = 0; i < numberOfLine; i++)
        {
            Vector3 position = new Vector3(0, 0, 0);
            var line = Instantiate(linePrefab, position, Quaternion.identity, lineRoot);
            var comp = line.GetComponent<Line>();
            comp.origin = tracking.handPoints[handConnections[i, 0]].transform;
            comp.destination = tracking.handPoints[handConnections[i, 1]].transform;
        }
    }
}
