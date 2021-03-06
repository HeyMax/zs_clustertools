import os,sys

def ssh_info_generate(cluster_uuid_list=[]):
	query1 = 'echo "select managementIp from HostVO where hypervisorType = \'KVM\''
	query2 = ';"| mysql -u root -pzstack.mysql.password zstack|grep -v managementIp'
	query = query1 + query2
	#mysql select statement
	if len(cluster_uuid_list):
		insert = ' and clusterUuid = \'' + cluster_uuid_list[0] + '\''
	if len(cluster_uuid_list) == 1 and cluster_uuid_list != 'all':
		query = query1 + insert + query2
	if len(cluster_uuid_list) > 1:		
		for index in range(1,len(cluster_uuid_list)):
			insert = insert + ' or clusterUuid = \'' + cluster_uuid_list[index] + '\''
		query = query1 + insert + query2
	
	#get_host_ips_str
	#host_ip_list = os.popen('echo "select managementIp from HostVO where hypervisorType = \'KVM\';"| mysql -u root -pzstack.mysql.password zstack|grep -v managementIp').read()
	host_ip_list = os.popen(query).read()
	host_ips = host_ip_list.split("\n")[:-1]

	#get_host_usernames_str
	host_username_list = os.popen('echo "select username,password from KVMHostVO;"| mysql -u root -pzstack.mysql.password zstack|grep -v username').read()
	host_usernames_list = host_username_list.split("\n")
	host_usernames = []
	for host_username in host_usernames_list:
		host_usernames.append(host_username.split("\t"))
	host_usernames = host_usernames[:-1]
	#same_len
	if len(host_usernames) < len(host_ips):
		Dvalue = len(host_ips) - len(host_usernames)
		while Dvalue > 0:
			host_usernames.append(["",""])
			Dvalue -= 1

	#create_kv_username_password
	count = 0
	userpassword_kvs = []
	while count < len(host_ips):
		userpassword_kvs.append("".join(host_ips[count]+" ansible_ssh_user=" + host_usernames[count][0] + " ansible_ssh_private_key_file=/usr/local/zstack/apache-tomcat/webapps/zstack/WEB-INF/classes/ansible/rsaKeys/id_rsa" ))
		count += 1
	#mn_ip=os.popen('cat /usr/local/zstack/apache-tomcat/webapps/zstack/WEB-INF/classes/zstack.properties |grep management').read().split(' = ')[1].split("\n")[0]
	#print mn_ip
	kvs_str = "\n".join(userpassword_kvs)
	# + "\n" +mn_ip+ " ansible_ssh_user=root ansible_ssh_private_key_file=/usr/local/zstack/apache-tomcat/webapps/zstack/WEB-INF/classes/ansible/rsaKeys/id_rsa"
	return kvs_str

def get_cluster_uuid_list():
	cluster_uuid_list = []
	if len(sys.argv) == 2:
		if sys.argv[1] != 'all':
			for cluster_uuid in sys.argv[1].split(","):
				cluster_uuid_list.append(cluster_uuid)
	return cluster_uuid_list

if __name__ == '__main__':
	file_asbc = open('inventory','w')
	file_asbc.write(ssh_info_generate(get_cluster_uuid_list()))
	file_asbc.close()
	# os.system("sort -k2n inventory|uniq")
