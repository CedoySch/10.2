import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QMessageBox, QTextEdit, QSizePolicy,
    QGroupBox, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ElectrostaticFieldApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Визуализация электростатического поля')
        self.setGeometry(100, 100, 1200, 700)

        instructions_label = QLabel('Введите параметры зарядов (x y q) в каждой строке:')
        instructions_label.setAlignment(Qt.AlignLeft)

        self.charges_input = QTextEdit()
        self.charges_input.setPlaceholderText("Пример:\n0 0 1\n1 0 -1")
        self.charges_input.setFixedHeight(150)

        grid_group = QGroupBox("Параметры сетки")
        grid_layout = QGridLayout()

        self.grid_min_input = QLineEdit("-10")
        self.grid_max_input = QLineEdit("10")
        self.grid_points_input = QLineEdit("200")

        grid_layout.addWidget(QLabel("Мин X и Y:"), 0, 0)
        grid_layout.addWidget(self.grid_min_input, 0, 1)
        grid_layout.addWidget(QLabel("Макс X и Y:"), 1, 0)
        grid_layout.addWidget(self.grid_max_input, 1, 1)
        grid_layout.addWidget(QLabel("Количество точек:"), 2, 0)
        grid_layout.addWidget(self.grid_points_input, 2, 1)

        grid_group.setLayout(grid_layout)

        self.plot_button = QPushButton('Построить поле')
        self.plot_button.clicked.connect(self.plot_field)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        input_layout = QVBoxLayout()
        input_layout.addWidget(instructions_label)
        input_layout.addWidget(self.charges_input)
        input_layout.addWidget(grid_group)
        input_layout.addWidget(self.plot_button)
        input_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(input_layout, 1)
        main_layout.addWidget(self.canvas, 3)

        self.setLayout(main_layout)
        self.show()

    def plot_field(self):
        try:
            charges_text = self.charges_input.toPlainText().strip()
            if not charges_text:
                raise ValueError("Необходимо ввести хотя бы один заряд.")

            charges = []
            for idx, line in enumerate(charges_text.split('\n'), start=1):
                if not line.strip():
                    continue
                parts = line.strip().split()
                if len(parts) != 3:
                    raise ValueError(f"Строка {idx}: Ожидается три значения (x y q).")
                x_str, y_str, q_str = parts
                try:
                    x, y, q = float(x_str), float(y_str), float(q_str)
                except ValueError:
                    raise ValueError(f"Строка {idx}: x, y и q должны быть числами.")
                charges.append((x, y, q))

            if not charges:
                raise ValueError("Необходимо ввести хотя бы один заряд.")

            try:
                grid_min = float(self.grid_min_input.text())
                grid_max = float(self.grid_max_input.text())
                grid_points = int(self.grid_points_input.text())
                if grid_min >= grid_max:
                    raise ValueError("Мин должно быть меньше Макс.")
                if grid_points <= 0:
                    raise ValueError("Количество точек должно быть положительным.")
            except ValueError as ve:
                raise ValueError(f"Параметры сетки: {ve}")

            self.figure.clear()
            ax = self.figure.add_subplot(111)

            x = np.linspace(grid_min, grid_max, grid_points)
            y = np.linspace(grid_min, grid_max, grid_points)
            X, Y = np.meshgrid(x, y)
            Ex = np.zeros_like(X)
            Ey = np.zeros_like(Y)

            for charge in charges:
                x0, y0, q = charge
                dx = X - x0
                dy = Y - y0
                r_squared = dx**2 + dy**2
                mask = r_squared < 0.1
                r_squared[mask] = 0.1
                r = np.sqrt(r_squared)
                Ex += q * dx / (r_squared * r)
                Ey += q * dy / (r_squared * r)

            ax.streamplot(X, Y, Ex, Ey, color='k', density=1.5, linewidth=0.5, arrowsize=1)

            plotted_positive = False
            plotted_negative = False
            for charge in charges:
                x0, y0, q = charge
                if q > 0 and not plotted_positive:
                    ax.plot(x0, y0, 'ro', markersize=8, label='Положительный заряд')
                    plotted_positive = True
                elif q < 0 and not plotted_negative:
                    ax.plot(x0, y0, 'bo', markersize=8, label='Отрицательный заряд')
                    plotted_negative = True
                elif q > 0:
                    ax.plot(x0, y0, 'ro', markersize=8)
                elif q < 0:
                    ax.plot(x0, y0, 'bo', markersize=8)

            ax.set_xlim(grid_min, grid_max)
            ax.set_ylim(grid_min, grid_max)
            ax.set_aspect('equal')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title('Электростатическое поле')
            ax.grid(True)

            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                          fancybox=True, shadow=True, ncol=2)

            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


def main():
    app = QApplication(sys.argv)
    ex = ElectrostaticFieldApp()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
