from neo4j.v1 import GraphDatabase, basic_auth

import geoip

def import_from_csv(self, asn, skip, limit):
	 session = self.driver.session()
	 result = session.run("MATCH (n) WHERE n.asn = {asn} RETURN n SKIP {skip} LIMIT {limit}", {"asn":asn, "skip":skip, "limit":limit})
	 session.close()

	 result_list = []
	 for record in result:
		 result_list.append(record["n"].properties)

	 return json.dumps(result_list)
