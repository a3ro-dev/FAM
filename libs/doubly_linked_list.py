class Node:
    """
    Represents a single node in a doubly-linked list.
    
    Attributes:
    - data (str): The data stored in the node.
    - next (Node): A reference to the next node in the list.
    - previous (Node): A reference to the previous node in the list.
    """
    
    def __init__(self, data: str, next: 'Node' = None, previous: 'Node' = None): #type: ignore
        """
        Initializes a new Node with the given data.
        
        Args:
        - data (str): The data to store in the node.
        - next (Node): A reference to the next node in the list.
        - previous (Node): A reference to the previous node in the list.
        """
        self.data = data
        self.next = next
        self.previous = previous


class DoublyLinkedList:
    """
    Methods:
    - __init__(): Initializes a new empty doubly-linked list.
    - insert_at_start(data: str): Inserts a new node with the given data at the beginning of the list.
    - to_list() -> list: Builds and returns a list representing the contents of the list from head to tail.
    - insert_at_end(data: str): Inserts a new node with the given data at the end of the list.
    - search(key: str) -> bool: Searches for a node with the given key in the list.
    """
    
    def __init__(self):
        """Initializes a new empty doubly-linked list."""
        self.head = None
    
    def insert_at_start(self, data: str) -> None:
        """
        Inserts a new node with the given data at the beginning of the list.
        
        Args:
        - data (str): The data to store in the new node.
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            self.head.previous = new_node
            new_node.next = self.head
            self.head = new_node
    
    def to_list(self) -> list:
        """
        Builds and returns a list representing the contents of the list from head to tail.
        
        Returns:
        - list: A list of node data from head to tail.
        """
        result = []
        temp = self.head
        while temp is not None:
            result.append(temp.data)
            temp = temp.next
        return result
    
    def insert_at_end(self, data: str) -> None:
        """
        Inserts a new node with the given data at the end of the list.
        
        Args:
        - data (str): The data to store in the new node.
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        
        temp = self.head
        while temp.next is not None:
            temp = temp.next
        
        temp.next = new_node
        new_node.previous = temp
    
    def search(self, key: str) -> bool:
        """
        Searches for a node with the given key in the list.
        
        Args:
        - key (str): The data to search for in the list.
        
        Returns:
        - bool: True if the key is found, False otherwise.
        """
        temp = self.head
        while temp is not None:
            if temp.data == key:
                print(f"KEY FOUND: {key}")
                return True
            temp = temp.next
        
        print("KEY NOT FOUND")
        return False


# # Example usage
# if __name__ == "__main__":
#     try:
#         dll = DoublyLinkedList()
#         a = str(input("Please enter the 1st value that you would like to insert at the start.\n"))
#         dll.insert_at_start(a)
#         b = str(input("Please enter the 2nd value that you would like to insert at the start.\n"))
#         dll.insert_at_start(b)
#         c = str(input("Please enter the 3rd value that you would like to insert at the end.\n"))
#         dll.insert_at_end(c)
        
#         prstr(dll.to_list())
#         d = str(input("Please enter the value that you would like to be searched for.\n"))
#         dll.search(d)
#     except Exception as e:
#         prstr(e)
#     finally:
#         prstr("Doubly Linked List Finished!")