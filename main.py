import sys
import json
import os
from importlib.metadata import version, PackageNotFoundError
import mssql_python
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFormLayout,
    QProgressBar,
    QDialog,
    QDialogButtonBox,
    QComboBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


def get_version():
    """Read version from package metadata or pyproject.toml"""
    try:
        return version("srodbpatch")
    except PackageNotFoundError:
        pass

    try:
        import tomllib

        pyproject_path = os.path.join(os.path.dirname(__file__), "pyproject.toml")
        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)
        return pyproject["project"]["version"]
    except Exception as e:
        raise RuntimeError(
            "Could not determine version. Please ensure:\n"
            "1. Package is installed with 'uv pip install -e .', or\n"
            "2. pyproject.toml is accessible in the application directory.\n"
            f"Error: {e}"
        )


__VERSION__ = get_version()


# Patch definitions - each patch is a list of SQL statements
PATCHES = {
    "Level 120 Skills": {
        "description": "Enable all level 120 skills by setting Service = 1",
        "backup_tables": ["_RefSkill"],
        "sql_statements": [
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 1 AND 273",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 276 AND 3481",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 3486 AND 3491",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 3493 AND 8321",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 8328 AND 8328",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 8331 AND 12176",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12178 AND 12186",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12188 AND 12196",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12198 AND 12199",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12201 AND 12206",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12210 AND 12216",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12218 AND 12222",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12225 AND 12306",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 12323 AND 20309",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 20311 AND 20501",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 20503 AND 21266",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 21268 AND 29693",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 29696 AND 30897",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 31038 AND 31086",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 31088 AND 31103",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 31105 AND 31181",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 31190 AND 31196",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 31198 AND 31924",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 32088 AND 32874",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 32891 AND 32894",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 32897 AND 32904",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33042 AND 33045",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33072 AND 33073",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33072 AND 33073",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33077 AND 33287",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33289 AND 33294",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33296 AND 33300",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33302 AND 33307",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33309 AND 33312",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33314 AND 33338",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33340 AND 33347",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33349 AND 33372",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33374 AND 33382",
            "UPDATE dbo._RefSkill SET Service = 1 WHERE ID BETWEEN 33740 AND 33785",
            "UPDATE dbo._RefSkill SET Service = 0 WHERE ID BETWEEN 7182 AND 7184",
            "UPDATE dbo._RefSkill SET Service = 0 WHERE ID BETWEEN 3436 AND 3440",
            "UPDATE dbo._RefSkill SET Service = 0 WHERE ID BETWEEN 5409 AND 5409",
        ],
    },
    "Add Silk to All Players": {
        "description": "Add 10,000 Silk to all active player accounts",
        "backup_tables": ["_Char"],
        "sql_statements": [
            """INSERT INTO SRO_VT_ACCOUNT.dbo.SK_Silk (JID, silk_own, silk_gift, silk_point)
SELECT JID, 10000, 0, 0
FROM SRO_VT_ACCOUNT.dbo.TB_User
WHERE JID NOT IN (SELECT JID FROM SRO_VT_ACCOUNT.dbo.SK_Silk)""",
            """UPDATE SRO_VT_ACCOUNT.dbo.SK_Silk
SET silk_own = silk_own + 10000
WHERE JID IN (SELECT JID FROM SRO_VT_ACCOUNT.dbo.TB_User)""",
        ],
    },
    "Add gold to all characters": {
        "description": "Add 99.000.000 gold to all characters",
        "backup_tables": ["_Char"],
        "sql_statements": [
            "UPDATE dbo._Char SET RemainGold = RemainGold + 99000000 WHERE CharID > 0",
        ],
    },
    "Reset Character Stats": {
        "description": "Reset all character stats to base values and refund stat points",
        "backup_tables": ["_Char"],
        "sql_statements": [
            """UPDATE dbo._Char
SET Strength = 20 + (MaxLevel - 1),
    Intellect = 20 + (MaxLevel - 1),
    RemainStatPoint = (MaxLevel - 1) * 3
WHERE CharID > 0""",
        ],
    },
}


class DatabaseSettingsDialog(QDialog):
    """Dialog for configuring database connection settings."""

    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Database Connection Settings")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.server_input = QLineEdit(current_settings.get("server", "localhost"))
        form_layout.addRow("Server:", self.server_input)

        self.port_input = QLineEdit(str(current_settings.get("port", 1433)))
        form_layout.addRow("Port:", self.port_input)

        self.database_input = QLineEdit(
            current_settings.get("database", "SRO_VT_SHARD")
        )
        form_layout.addRow("Database:", self.database_input)

        self.user_input = QLineEdit(current_settings.get("user", "sa"))
        form_layout.addRow("User:", self.user_input)

        self.password_input = QLineEdit(current_settings.get("password", ""))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_settings(self):
        """Return the configured settings."""
        return {
            "server": self.server_input.text().strip(),
            "port": int(self.port_input.text().strip()),
            "database": self.database_input.text().strip(),
            "user": self.user_input.text().strip(),
            "password": self.password_input.text(),
        }


class BackupWorker(QThread):
    """Worker thread to create backup of specified tables."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, db_config, tables):
        super().__init__()
        self.db_config = db_config
        self.tables = tables

    def run(self):
        """Create backup of specified tables."""
        try:
            conn = mssql_python.connect(self.db_config)
            cursor = conn.cursor()

            backup_info = []

            for table in self.tables:
                backup_table = f"{table}_Backup"
                self.progress.emit(f"Creating backup of {table}...")

                cursor.execute(f"""
                    IF OBJECT_ID('{backup_table}', 'U') IS NOT NULL
                        DROP TABLE {backup_table}
                """)

                cursor.execute(f"""
                    SELECT *
                    INTO {backup_table}
                    FROM {table}
                """)

                cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
                row_count = cursor.fetchone()[0]
                backup_info.append(f"{table}: {row_count} rows backed up")

            conn.commit()
            conn.close()

            self.finished.emit(
                True,
                "Backup created successfully!\n\n" + "\n".join(backup_info),
            )

        except Exception as e:
            self.finished.emit(False, f"Backup failed: {str(e)}")


class RestoreWorker(QThread):
    """Worker thread to restore from backup."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, db_config, tables):
        super().__init__()
        self.db_config = db_config
        self.tables = tables

    def run(self):
        """Restore tables from backup."""
        try:
            conn = mssql_python.connect(self.db_config)
            cursor = conn.cursor()

            self.progress.emit("Checking for backups...")

            for table in self.tables:
                backup_table = f"{table}_Backup"
                cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_NAME = '{backup_table}'
                """)
                if cursor.fetchone()[0] == 0:
                    raise Exception(f"No backup found for {table}!")

            restore_info = []

            for table in self.tables:
                backup_table = f"{table}_Backup"
                self.progress.emit(f"Restoring {table} from backup...")

                cursor.execute(f"DELETE FROM {table}")

                cursor.execute(f"""
                    INSERT INTO {table}
                    SELECT * FROM {backup_table}
                """)

                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                restore_info.append(f"{table}: {row_count} rows restored")

            conn.commit()
            conn.close()

            self.finished.emit(
                True,
                "Restore completed successfully!\n\n" + "\n".join(restore_info),
            )

        except Exception as e:
            self.finished.emit(False, f"Restore failed: {str(e)}")


class PatchWorker(QThread):
    """Worker thread to apply database patches."""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, db_config, patch_name, patch_config):
        super().__init__()
        self.db_config = db_config
        self.patch_name = patch_name
        self.patch_config = patch_config

    def run(self):
        """Execute the patch."""
        try:
            conn = mssql_python.connect(self.db_config)
            cursor = conn.cursor()

            # Check if backup exists
            self.progress.emit("Checking for backup...")
            backup_tables = self.patch_config["backup_tables"]
            backup_exists = True

            for table in backup_tables:
                backup_table = f"{table}_Backup"
                cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_NAME = '{backup_table}'
                """)
                if cursor.fetchone()[0] == 0:
                    backup_exists = False
                    break

            # Create backup if it doesn't exist
            if not backup_exists:
                self.progress.emit("Creating automatic backup...")
                for table in backup_tables:
                    backup_table = f"{table}_Backup"
                    cursor.execute(f"""
                        IF OBJECT_ID('{backup_table}', 'U') IS NOT NULL
                            DROP TABLE {backup_table}
                    """)
                    cursor.execute(f"""
                        SELECT *
                        INTO {backup_table}
                        FROM {table}
                    """)
                self.progress.emit("Backup created successfully")

            # Apply patch statements
            sql_statements = self.patch_config["sql_statements"]
            total_statements = len(sql_statements)
            rows_affected_total = 0

            for idx, sql in enumerate(sql_statements, 1):
                self.progress.emit(f"Executing statement {idx}/{total_statements}...")
                cursor.execute(sql)
                rows_affected = cursor.rowcount
                rows_affected_total += rows_affected

            self.progress.emit("Committing changes...")
            conn.commit()
            conn.close()

            summary = (
                f"Successfully applied patch '{self.patch_name}'!\n\n"
                f"Statements executed: {total_statements}\n"
                f"Total rows affected: {rows_affected_total}"
            )

            self.finished.emit(True, summary)

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            self.finished.emit(False, f"Error: {str(e)}\n\nDetails:\n{error_details}")


class DatabasePatchTool(QMainWindow):
    CONFIG_FILE = "db_config.json"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Database Patch Management Tool v{__VERSION__}")
        self.setGeometry(100, 100, 600, 480)
        self.setMinimumSize(600, 480)

        self.load_config()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Database Patch Management Tool")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Version label
        version_label = QLabel(f"Version {__VERSION__}")
        version_label.setStyleSheet("font-size: 9pt; color: #666; padding-bottom: 5px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Form layout for patch selection
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(15)

        # Patch selector
        patch_label = QLabel("Select Patch:")
        patch_label.setStyleSheet("font-size: 11pt;")
        self.patch_combo = QComboBox()
        self.patch_combo.setMinimumHeight(35)
        self.patch_combo.setStyleSheet("font-size: 11pt; padding: 5px;")

        for patch_name in PATCHES.keys():
            self.patch_combo.addItem(patch_name)

        self.patch_combo.currentTextChanged.connect(self.on_patch_selected)
        form_layout.addRow(patch_label, self.patch_combo)

        layout.addLayout(form_layout)

        # Patch description
        self.description_label = QLabel()
        self.description_label.setStyleSheet(
            "padding: 10px; background-color: #e7f3ff; border-radius: 5px; font-size: 10pt;"
        )
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        # Update description for initial selection
        self.on_patch_selected(self.patch_combo.currentText())

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Utility buttons
        button_layout = QHBoxLayout()

        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)

        self.settings_button = QPushButton("Database Settings")
        self.settings_button.clicked.connect(self.show_settings)
        button_layout.addWidget(self.settings_button)

        layout.addLayout(button_layout)

        # Backup/Restore buttons
        backup_layout = QHBoxLayout()

        self.backup_button = QPushButton("Create Backup")
        self.backup_button.clicked.connect(self.create_backup)
        self.backup_button.setStyleSheet("padding: 8px;")
        backup_layout.addWidget(self.backup_button)

        self.restore_button = QPushButton("Restore from Backup")
        self.restore_button.clicked.connect(self.restore_backup)
        self.restore_button.setStyleSheet("padding: 8px;")
        backup_layout.addWidget(self.restore_button)

        layout.addLayout(backup_layout)

        # Apply button
        apply_layout = QHBoxLayout()

        self.apply_button = QPushButton("Apply Patch")
        self.apply_button.clicked.connect(self.apply_patch)
        self.apply_button.setStyleSheet("padding: 10px; font-size: 12pt;")
        apply_layout.addWidget(self.apply_button)

        layout.addLayout(apply_layout)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.worker = None

    def on_patch_selected(self, patch_name):
        """Update description when patch is selected."""
        if patch_name in PATCHES:
            patch_config = PATCHES[patch_name]
            description = patch_config["description"]
            tables = ", ".join(patch_config["backup_tables"])
            self.description_label.setText(
                f"{description}\n\nAffected tables: {tables}"
            )

    def load_config(self):
        """Load database configuration from file or use defaults."""
        default_config = {
            "server": "localhost",
            "port": 1433,
            "database": "SRO_VT_SHARD",
            "user": "sa",
            "password": "",
        }

        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    config = json.load(f)
                self.server = config.get("server", default_config["server"])
                self.port = config.get("port", default_config["port"])
                self.database = config.get("database", default_config["database"])
                self.user = config.get("user", default_config["user"])
                self.password = config.get("password", default_config["password"])
            except Exception:
                self.server = default_config["server"]
                self.port = default_config["port"]
                self.database = default_config["database"]
                self.user = default_config["user"]
                self.password = default_config["password"]
        else:
            self.server = default_config["server"]
            self.port = default_config["port"]
            self.database = default_config["database"]
            self.user = default_config["user"]
            self.password = default_config["password"]

    def save_config(self):
        """Save database configuration to file."""
        config = {
            "server": self.server,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
        }
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            QMessageBox.warning(
                self, "Config Save Failed", f"Could not save configuration: {str(e)}"
            )

    def show_settings(self):
        """Show database settings dialog."""
        current_settings = {
            "server": self.server,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
        }

        dialog = DatabaseSettingsDialog(self, current_settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.server = new_settings["server"]
            self.port = new_settings["port"]
            self.database = new_settings["database"]
            self.user = new_settings["user"]
            self.password = new_settings["password"]
            self.save_config()

            QMessageBox.information(
                self,
                "Settings Saved",
                "Database connection settings have been saved.\n\n"
                "Click 'Test Connection' to verify the new settings.",
            )

    def get_connection_string(self):
        """Get the database connection string."""
        return (
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
        )

    def test_connection(self):
        """Test the database connection."""
        try:
            conn = mssql_python.connect(self.get_connection_string())
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            conn.close()

            QMessageBox.information(
                self,
                "Connection Success",
                f"Successfully connected to database!\n\nServer version:\n{version[0][:100]}...",
            )
            self.status_label.setText("Connection successful")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #d4edda; color: #155724;"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Failed", f"Failed to connect to database:\n{str(e)}"
            )
            self.status_label.setText(f"Connection failed: {str(e)}")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #f8d7da; color: #721c24;"
            )

    def create_backup(self):
        """Create backup of tables for current patch."""
        patch_name = self.patch_combo.currentText()
        if patch_name not in PATCHES:
            return

        patch_config = PATCHES[patch_name]
        tables = patch_config["backup_tables"]

        reply = QMessageBox.question(
            self,
            "Create Backup",
            f"This will create a backup for patch: {patch_name}\n\n"
            f"Tables to backup: {', '.join(tables)}\n\n"
            f"Existing backups will be replaced.\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.apply_button.setEnabled(False)
        self.test_button.setEnabled(False)
        self.backup_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setTextVisible(True)
        self.status_label.setText("Creating backup...")
        self.status_label.setStyleSheet(
            "padding: 10px; background-color: #fff3cd; color: #856404;"
        )

        self.worker = BackupWorker(self.get_connection_string(), tables)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_backup_finished)
        self.worker.start()

    def restore_backup(self):
        """Restore tables from backup for current patch."""
        patch_name = self.patch_combo.currentText()
        if patch_name not in PATCHES:
            return

        patch_config = PATCHES[patch_name]
        tables = patch_config["backup_tables"]

        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            f"WARNING: This will restore tables for patch: {patch_name}\n\n"
            f"Tables to restore: {', '.join(tables)}\n\n"
            f"ALL current data in these tables will be DELETED and replaced with backup data.\n\n"
            f"This cannot be undone. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.apply_button.setEnabled(False)
        self.test_button.setEnabled(False)
        self.backup_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setTextVisible(True)
        self.status_label.setText("Restoring from backup...")
        self.status_label.setStyleSheet(
            "padding: 10px; background-color: #fff3cd; color: #856404;"
        )

        self.worker = RestoreWorker(self.get_connection_string(), tables)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_restore_finished)
        self.worker.start()

    def apply_patch(self):
        """Apply the selected patch."""
        patch_name = self.patch_combo.currentText()
        if patch_name not in PATCHES:
            return

        patch_config = PATCHES[patch_name]

        reply = QMessageBox.question(
            self,
            "Confirm Patch",
            f"This will apply patch: {patch_name}\n\n"
            f"{patch_config['description']}\n\n"
            f"A backup will be created automatically before applying.\n"
            f"You can restore from backup at any time.\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.apply_button.setEnabled(False)
        self.test_button.setEnabled(False)
        self.backup_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.status_label.setText("Applying patch...")
        self.status_label.setStyleSheet(
            "padding: 10px; background-color: #fff3cd; color: #856404;"
        )

        self.worker = PatchWorker(
            self.get_connection_string(), patch_name, patch_config
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_patch_finished)
        self.worker.start()

    def on_progress(self, message):
        """Handle progress updates from worker."""
        self.status_label.setText(message)

    def on_backup_finished(self, success, message):
        """Handle backup completion."""
        self.apply_button.setEnabled(True)
        self.test_button.setEnabled(True)
        self.backup_button.setEnabled(True)
        self.restore_button.setEnabled(True)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        if success:
            QMessageBox.information(self, "Backup Complete", message)
            self.status_label.setText("Backup created successfully")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #d4edda; color: #155724;"
            )
        else:
            QMessageBox.critical(self, "Backup Failed", message)
            self.status_label.setText("Backup failed")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #f8d7da; color: #721c24;"
            )

    def on_restore_finished(self, success, message):
        """Handle restore completion."""
        self.apply_button.setEnabled(True)
        self.test_button.setEnabled(True)
        self.backup_button.setEnabled(True)
        self.restore_button.setEnabled(True)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        if success:
            QMessageBox.information(self, "Restore Complete", message)
            self.status_label.setText("Restore completed successfully")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #d4edda; color: #155724;"
            )
        else:
            QMessageBox.critical(self, "Restore Failed", message)
            self.status_label.setText("Restore failed")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #f8d7da; color: #721c24;"
            )

    def on_patch_finished(self, success, message):
        """Handle patch completion."""
        self.apply_button.setEnabled(True)
        self.test_button.setEnabled(True)
        self.backup_button.setEnabled(True)
        self.restore_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        if success:
            QMessageBox.information(self, "Patch Applied", message)
            self.status_label.setText("Patch applied successfully")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #d4edda; color: #155724;"
            )
        else:
            QMessageBox.critical(self, "Patch Failed", message)
            self.status_label.setText("Patch failed")
            self.status_label.setStyleSheet(
                "padding: 10px; background-color: #f8d7da; color: #721c24;"
            )


def main():
    app = QApplication(sys.argv)
    window = DatabasePatchTool()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
