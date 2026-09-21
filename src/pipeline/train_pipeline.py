from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.logger import logger


class TrainPipeline:
    """Orchestrates the three stages in order: ingest -> transform -> train."""

    def __init__(self):
        self.data_ingestion = DataIngestion()
        self.data_transformation = DataTransformation()
        self.model_trainer = ModelTrainer()

    def run(self) -> dict:
        logger.info("Starting full training pipeline")
        train_path, test_path = self.data_ingestion.initiate_data_ingestion()

        train_arr, test_arr, _ = self.data_transformation.initiate_data_transformation(
            train_path, test_path
        )

        report = self.model_trainer.initiate_model_trainer(train_arr, test_arr)
        logger.info("Training pipeline finished")
        return report


if __name__ == "__main__":
    result = TrainPipeline().run()
    print("\nRESULT")
    for k, v in result.items():
        print(f"  {k}: {v}")