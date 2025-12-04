import tkinter as tk
from gui import IMSApp


def main() -> None:
    root = tk.Tk()
    IMSApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
