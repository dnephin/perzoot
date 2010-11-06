#
# Deployment Script for Perzoot website_main
#
# Usage:
#	./deploy <checkout> <env>
#	
#	checkout:	path to the root of the jobsite_web checkout
#	env:		stage | prod
#

HTTPD_SITES=/etc/apache2/sites-enabled/


if [ ! $1 ]; then
	echo "No checkout dir specified. See usage."
	exit -1
fi

if [ ! $2 ]; then
	echo "No environment specified. See usage. "
	exit -1
fi

case $2 in
	"stage")
		DEPLOY_ENV=/var/pz_stage
		CONF_DIR=$1/conf/stage
		;;
	"prod")
		DEPLOY_ENV=/var/perzoot
		CONF_DIR=$1/conf/prod
		;;
	*)
		echo "Unknown environment $1. Should be stage or prod."
		exit -2
		;;
esac


# Copy apache config into sites
cp $CONF_DIR/$1.conf $HTTPD_SITES
cp $CONF_DIR/django.wsgi $HTTPD_SITES

# Copy code
rsync --delete --exclude=.git --exclude=*.pyc --exclude=*.swp $1/jobsite_web $DEPLOY_ENV/jobsite_web
# Copy media
rsync --delete --exclude=.git --exclude=*.pyc --exclude=*.swp $1/ $DEPLOY_ENV/jobsite_web

# Copy settings and url
cp $CONF_DIR/settings.py $DEPLOY_ENV/jobsite_web/

# restart apache2
sudo service apache2 restart
