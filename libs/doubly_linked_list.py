class Node(object):
    
    # Represents a single node in a doubly-linked list.
    
    # Attributes:
    # - data (int): The data stored in the node.
    # - next (Node): A reference to the next node in the list.
    # - previous (Node): A reference to the previous node in the list.
        
    def __init__(self, data, next=None, previous=None):
        
        # Initializes a new Node with the given data.
        
        # Args:
        # - data (int): The data to store in the node.
        # - next (Node): A reference to the next node in the list.
        # - previous (Node): A reference to the previous node in the list.
        
        self.data = data
        self.next = next
        self.previous = previous
        
class DoublyLinkedList(object):
    
    # Represents a doubly-linked list.
    
    # Attributes:
    # - head (Node): A reference to the first node in the list.
        
    def __init__(self):
            
        # Initializes a new empty doubly-linked list.
            
        self.head = None
            
    def insertAtStart(self, data):
        
        # Inserts a new node with the given data at the beginning of the list.
        
        # Args:
        # - data (int): The data to store in the new node.
            
        if self.head == None:
            newNode = Node(data)
            self.head = newNode
        else:
            newNode = Node(data)
            self.head.previous = newNode
            newNode.next = self.head
            self.head = newNode
            
    # def insertInBetween(self, previous, data):
    #     if previous == None:
    #         print("This node doesn't exist in DLL")
    #         return
        
    #     newNode = Node(data)
    #     newNode.next = previous.next
    #     previous.next = newNode
    #     newNode.previous = previous
    #     if newNode.next != None:
    #         newNode.next.previous = newNode  
        
    def to_list(self):
        # Builds and returns a list representing the contents of the list from head to tail.
        
        result = []
        temp = self.head
            
        while(temp != None):
            result.append(temp.data)
            temp = temp.next
        
        return result
            
    def insertAtEnd(self, data):
        
        # Inserts a new node with the given data at the end of the list.
        
        # Args:
        # - data (int): The data to store in the new node.
        
        newNode = Node(data)
            
        temp = self.head
        while(temp.next != None):
            temp = temp.next
                
        temp.next = newNode
        newNode.previous = temp


    def searchDLList(self, key):
        
        # Searches for a node with the given key in the list.
        # Prints a message indicating whether the key was found or not.

        # Args:
        # - key (int): The data to search for in the list.    
        
        temp = self.head
            
        while(temp):
            if temp.data == key:
                print(f"KEY FOUND\n {key}")
                return key
            temp = temp.next
            
        print("KEY NOT FOUND")
                
# if __name__ == "__main__":
    
#    try:
#         dll = DoublyLinkedList()

#         a = int(input("Please enter the 1st value that you would like to insert at the start.\n"))
#         dll.insertAtStart(a)
#         b = int(input("Please enter the 2nd value that you would like to insert at the start.\n"))
#         dll.insertAtStart(b)
#         c = int(input("Please enter the 3rd value that you would like to insert at the end.\n"))
#         dll.insertAtEnd(c)
        
#         dll.printDLL()
#         d = int(input("Please enter the value that you would like to be searched for.\n"))
#         dll.searchDLList(d)
        
#    except Exception as e:
#        print(e)
 
#    finally:
#        print("Doubly Linked List Finished!")