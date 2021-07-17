import aioboto3
import botocore.exceptions
import json
import logging
from opentelemetry import trace
import time

from aggregators import AggregationResult
from base.config import settings
from base.json import DataClassJSONEncoder

tracer = trace.get_tracer(__name__)


class AggregationResultSaver():
    """
    Saves aggregation results somewhere (hint: it's on S3)
    """
    def __init__(self):
        pass

    async def save_aggregation_result(self, station_id, aggregation_result: AggregationResult):
        if not settings.s3.enabled:
            pass
        else:
            try:
                with tracer.start_as_current_span("save_aggregation_result"):
                    await self._save_results(station_id, aggregation_result)
                    # Later
                    """
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(
                        self.executor,
                        functools.partial(
                            self._save_results,
                            station_id,
                            aggregation_result
                        )
                    )
                    """
            except botocore.exceptions.BotoCoreError as e:
                # Don't error out here, just log a warning.
                # Aggregation was still successful, we just can't gather stats.
                logging.warning("Could not save aggregation results on S3")
                logging.exception(e)
            except botocore.exceptions.ClientError as e:
                # Don't error out here, just log a warning.
                # Aggregation was still successful, we just can't gather stats.
                logging.warning("Could not save aggregation results on S3")
                logging.exception(e)

    async def _save_results(self, station_id, aggregation_result: AggregationResult):
        logging.info(f"Saving aggregated data for {station_id} to S3")
        session = aioboto3.Session()
        async with session.resource("s3", endpoint_url=settings.s3.endpoint_url) as s3:
            timestamp = int(time.time())
            bucket = await s3.Bucket(settings.s3.bucket_name)
            key = f"{station_id}/{timestamp}/extracted.json"
            await bucket.put_object(
                Key=key,
                Body=json.dumps(aggregation_result.items, cls=DataClassJSONEncoder)
            )
            for source in aggregation_result.sources:
                if isinstance(source.data, str):
                    extension = "txt"
                    body = source.data
                else:
                    extension = "json"
                    body = json.dumps(source.data)
                key = f"{station_id}/{timestamp}/sources/{source.type}/data.{extension}"
                await bucket.put_object(
                    Key=key,
                    Body=body
                )
