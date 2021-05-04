import React, {Component} from 'react';
import {withStyles} from '@material-ui/core/styles';
import {withRouter, matchPath} from "react-router";

import {
    Paper,
    Container,
    Button,
    Grid,
    Backdrop,
    CircularProgress
} from '@material-ui/core';

import _ from 'lodash';
import moment from 'moment';
import ContactInfo from './components/ContactInfo';
import Donations from './components/Donations';
import AnimalInfo from './components/AnimalInfo';
import VolunteerActivity from './components/VolunteerActivity';
import VolunteerHistory from './components/VolunteerHistory';


const customStyles = theme => ({
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
        color: '#fff',
    },
    stickyContainer: {
        position: 'fixed',
        paddingTop: 25
    }
});

class View360 extends Component {
    constructor(props) {
        super(props);

        this.state = {
            participantData: {},
            animalData: {},
            adoptionEvents: {},
            fosterEvents: {},
            matchId: undefined,
            isDataBusy: false,
        }

        this.onBackClick = this.onBackClick.bind(this);
        this.extractVolunteerActivity = this.extractVolunteerActivity.bind(this);
    }

    async componentDidMount() {
        this.setState({
            isDataBusy: true,
            showSearchBar: false,
            matchId: _.last(this.props.location.pathname.split('/'))
        });

        await new Promise(resolve => setTimeout(resolve, 1000));
        let response = await fetch(`/api/360/${this.state.matchId}`);
        response = await response.json();

        let animalInfo = await fetch(`/api/person/${this.state.matchId}/animals`);
        animalInfo = await animalInfo.json()
        const animalIds = _.keys(animalInfo);

        let adoptionEvents = {};
        let fosterEvents = {};

        for (let id of animalIds) {
            this.getAnimalEvents(id, this.state.matchId).then((events) => {
                adoptionEvents[id] = _.filter(events[id], function(e) {
                    return e["Type"] && e["Type"].toLowerCase().includes("adopt");
                });
                fosterEvents[id] = _.filter(events[id], function(e) {
                    return e["Type"] && e["Type"].toLowerCase().includes("foster");
                });
            })
        }

        this.setState({
            participantData: response.result,
            animalData: animalInfo,
            adoptionEvents: adoptionEvents,
            fosterEvents: fosterEvents,
            isDataBusy: false
        });
    }

    async getAnimalEvents(animalId, matchId) {
        let response = await fetch(`/api/person/${matchId}/animal/${animalId}/events`);
        return await response.json()
    }

    extractVolunteerActivity() {
        const volgistics = _.find(this.state.participantData.contact_details, {"source_type": "volgistics"}) || {};
        let volunteerActivity = {"life_hours": 0, "ytd_hours": 0, "start_date": "N/A"}

        if (Object.keys(volgistics).length > 0) {
            const volgisticsJson = JSON.parse(volgistics.json);
            volunteerActivity = _.pick(volgisticsJson, Object.keys(volunteerActivity));
            if (volunteerActivity["start_date"] !== "") {
                volunteerActivity["start_date"] = moment(volunteerActivity["start_date"], "MM-DD-YYYY").format("YYYY-MM-DD");
            }
        }
        return volunteerActivity;
    }

    onBackClick() {
        const match = matchPath(`/360view/search`, {
            path: "/360view/search",
            exact: true
        });

        this.props.history.push(match.url, this.props.location.state.state);

    }

    render() {
        const {classes} = this.props;

        return (
            <Container>
                {(_.isEmpty(this.state.participantData) !== true &&
                    this.state.isDataBusy !== true && (
                        <Paper elevation={1} style={{"padding": "2em"}}>
                            <Grid container justify={"center"}>
                                <Grid item sm={4}>
                                    <Grid sm={2} className={classes.stickyContainer} container direction="column"
                                          alignItems={"center"}>
                                        <Grid item>
                                            <ContactInfo
                                                participant={_.get(this.state, 'participantData.contact_details')}/>
                                        </Grid>
                                        <Grid item style={{"padding": "1em"}}>
                                            <Button elevation={2} variant="contained" color="primary"
                                                    onClick={() => {this.onBackClick()}}>Back to Results
                                            </Button>
                                        </Grid>
                                    </Grid>

                                </Grid>
                                <Grid item sm>
                                    <Grid container direction="column" style={{"marginTop": "1em"}}>
                                        <Donations donations={_.get(this.state, 'participantData.donations')}/>
                                        <AnimalInfo pets={_.get(this.state, 'animalData')} 
                                                    events={_.get(this.state, 'adoptionEvents')} 
                                                    headerText={"Adoption Records"}
                                        />
                                        <AnimalInfo pets={_.get(this.state, 'animalData')}
                                                    events={_.get(this.state, 'fosterEvents')} 
                                                    headerText={"Foster Records"}
                                        />
                                        <VolunteerActivity volunteer={this.extractVolunteerActivity()} />
                                        <VolunteerHistory volunteerShifts={_.get(this.state, 'participantData.shifts')} />
                                    </Grid>
                                </Grid>
                            </Grid>
                        </Paper>))}
                {this.state.isDataBusy === true && (
                    <Backdrop className={classes.backdrop} open={this.state.isLoading !== false}>
                        <CircularProgress size={60}/>
                    </Backdrop>
                )}
            </Container>
        );
    }
}

export default withRouter(withStyles(customStyles)(View360));