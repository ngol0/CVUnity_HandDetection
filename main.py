import cv2 as cv
import cvzone
import socket
from cvzone.HandTrackingModule import HandDetector

class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.8, server_ip="127.0.0.1", server_port=5052):
        """
        Initialize hand tracker with camera and network settings
        
        Args:
            max_hands (int): Maximum number of hands to detect
            detection_confidence (float): Minimum confidence for hand detection
            server_ip (str): IP address of Unity server
            server_port (int): Port number for Unity communication
        """
        # Camera setup
        self.cap = cv.VideoCapture(0)
        self.cap.set(3, 1280)  # Width
        self.cap.set(4, 720)   # Height
        
        # Get frame dimensions
        success, img = self.cap.read()
        if success:
            self.h, self.w, _ = img.shape
            print(f"Camera initialized: {self.w}x{self.h}")
        else:
            raise Exception("Failed to initialize camera")
        
        # Hand detector setup
        self.hand_detector = HandDetector(maxHands=max_hands, detectionCon=detection_confidence)
        print(f"Hand detector initialized: max_hands={max_hands}, confidence={detection_confidence}")
        
        # Network setup
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address_port = (server_ip, server_port)
        print(f"Network initialized: {server_ip}:{server_port}")
    
    def process_hand_landmarks(self, landmark_list):
        """
        Process hand landmarks and convert to Unity coordinate system
        
        Args:
            landmark_list (list): List of hand landmarks from MediaPipe
            
        Returns:
            list: Flattened list of coordinates [x1, y1, z1, x2, y2, z2, ...]
        """
        data = []
        for lm in landmark_list:
            # Convert coordinates:
            # - Keep x as is
            # - Flip y coordinate (OpenCV uses top-left origin, Unity uses bottom-left)
            # - Keep z as relative depth
            data.extend([lm[0], self.h - lm[1], lm[2]])
        
        return data
    
    def send_data_to_unity(self, data):
        """
        Send hand landmark data to Unity via UDP
        
        Args:
            data (list): Hand landmark coordinates to send
        """
        try:
            # Convert data to string and send
            data_string = str(data)
            self.sock.sendto(str.encode(data_string), self.server_address_port)
            #print(f"Sent {len(data)//3} landmarks to Unity")
        except Exception as e:
            print(f"Error sending data to Unity: {e}")
    
    def process_frame(self):
        """
        Process a single camera frame for hand detection
        
        Returns:
            tuple: (success, processed_image, hand_data)
                success (bool): Whether frame was captured successfully
                processed_image (numpy.ndarray): Image with hand annotations
                hand_data (list): Hand landmark coordinates (empty if no hands)
        """
        success, img = self.cap.read()
        if not success:
            return False, None, []
        
        data = []
        
        # Detect hands
        hands, img = self.hand_detector.findHands(img)
        
        if hands:
            hand = hands[0]  # Get first hand
            landmark_list = hand['lmList']
            
            # Process landmarks
            data = self.process_hand_landmarks(landmark_list)
            
            # Send to Unity
            self.send_data_to_unity(data)
        
        return True, img, data
    
    def run(self):
        """
        Main loop for hand tracking
        """
        print("Starting hand tracking loop...")
        print("Press 'q' to quit, 'ESC' to exit")
        
        while True:
            success, img, hand_data = self.process_frame()
            
            if not success:
                print("Failed to capture frame")
                break
            
            # Display image
            img = cv.resize(img, (0,0), None, 0.5, 0.5)  # Resize for better performance
            cv.imshow("Hand Tracking", img)
            
            # Handle keyboard input
            key = cv.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
        
        self.cleanup()
    
    def cleanup(self):
        """
        Clean up resources
        """
        print("Cleaning up...")
        self.cap.release()
        cv.destroyAllWindows()
        self.sock.close()
        print("Cleanup complete")

def create_hand_tracker(max_hands=1, detection_confidence=0.8, server_ip="127.0.0.1", server_port=5052):
    """
    Factory function to create and configure a HandTracker
    
    Args:
        max_hands (int): Maximum number of hands to detect
        detection_confidence (float): Minimum confidence for hand detection
        server_ip (str): IP address of Unity server
        server_port (int): Port number for Unity communication
        
    Returns:
        HandTracker: Configured hand tracker instance
    """
    try:
        tracker = HandTracker(max_hands, detection_confidence, server_ip, server_port)
        return tracker
    except Exception as e:
        print(f"Error creating hand tracker: {e}")
        return None

def main():
    """
    Main function to run the hand tracking application
    """
    print("=== Hand Tracking Application ===")
    
    # Configuration
    MAX_HANDS = 2
    DETECTION_CONFIDENCE = 0.8
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5052
    
    print(f"Configuration:")
    print(f"  Max hands: {MAX_HANDS}")
    print(f"  Detection confidence: {DETECTION_CONFIDENCE}")
    print(f"  Unity server: {SERVER_IP}:{SERVER_PORT}")
    print()
    
    # Create hand tracker
    tracker = create_hand_tracker(
        max_hands=MAX_HANDS,
        detection_confidence=DETECTION_CONFIDENCE,
        server_ip=SERVER_IP,
        server_port=SERVER_PORT
    )
    
    if tracker is None:
        print("Failed to initialize hand tracker")
        return
    
    try:
        # Run the tracker
        tracker.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if tracker:
            tracker.cleanup()


if __name__ == "__main__":
    main()