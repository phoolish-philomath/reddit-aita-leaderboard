$(document).ready(function(){
	    //connect to the socket server.
	    var socket = io.connect('http://' + document.domain + ':' + location.port + '/');

	    socket.on('leaderboard_update', (msg) => {
		let tableBodyHTML = '';
                let submissionData = {};
		let rowHTML = '';
		for (let i = 0; i < msg.top_submissions.length; i++) { 
	       submissionData = msg.top_submissions[i];
	       rowHTML = `<tr><td>${submissionData.rank}</td><td><a href="${submissionData.url}">${submissionData.title}</a></td></tr>`;
		tableBodyHTML += rowHTML;
		}
		$('#leaderboard-contents').html(tableBodyHTML);
		$('#last-updated').html("Last updated " + msg.update_time);
	    });
});
