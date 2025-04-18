from export import ExportDestination


class TelegramExportMixin:
    def export(self, destination: ExportDestination):
        destination.export(self._export_data)


class ResponseDataStatsMixin:
    def most_sings_per_performer(self):
        pass

    @property
    def found_data(self):
        return self._export_data

    @property
    def num_unique_songs(self):
        return sum(len(s) for s in self._export_data.values())
